from __future__ import annotations

import numpy as np

from core.control.conversions import (
    require_lti_model,
    require_scipy_signal,
    to_state_space,
    to_transfer_function,
)
from core.control.frequency_response import FrequencyResponseModel
from core.control.lti import is_lti_model
from core.errors.errors import RuntimeError as MathToolRuntimeError


def time_vector(value, function_name):
    try:
        vector = np.asarray(value, dtype=float).reshape(-1)
    except (TypeError, ValueError) as error:
        raise MathToolRuntimeError(
            f"{function_name}: time vector must be numeric"
        ) from error

    if vector.size == 0:
        raise MathToolRuntimeError(
            f"{function_name}: time vector cannot be empty"
        )

    if not np.all(np.isfinite(vector)):
        raise MathToolRuntimeError(
            f"{function_name}: time vector values must be finite"
        )

    if np.any(np.diff(vector) < 0):
        raise MathToolRuntimeError(
            f"{function_name}: time vector must be nondecreasing"
        )

    return vector


def frequency_vector(value, function_name):
    try:
        vector = np.asarray(value, dtype=float).reshape(-1)
    except (TypeError, ValueError) as error:
        raise MathToolRuntimeError(
            f"{function_name}: frequency vector must be numeric"
        ) from error

    if vector.size == 0:
        raise MathToolRuntimeError(
            f"{function_name}: frequency vector cannot be empty"
        )

    if not np.all(np.isfinite(vector)) or np.any(vector <= 0):
        raise MathToolRuntimeError(
            f"{function_name}: frequency vector must contain positive finite values"
        )

    return vector


def require_model(model, function_name):
    if not is_lti_model(model):
        raise MathToolRuntimeError(
            f"{function_name}: expected LTI model, got {type(model).__name__}"
        )


def transfer_coefficients(model, function_name):
    require_model(model, function_name)
    transfer_function = to_transfer_function(model)
    return (
        np.asarray(transfer_function.numerator, dtype=float),
        np.asarray(transfer_function.denominator, dtype=float),
        transfer_function,
    )


def step_response(model, t=None):
    signal = require_scipy_signal()
    numerator, denominator, tf_model = transfer_coefficients(model, "step")
    t_values = None if t is None else time_vector(t, "step")

    try:
        if tf_model.is_discrete:
            system = signal.dlti(numerator, denominator, dt=tf_model.Ts)
            tout, yout = signal.dstep(system, t=t_values)
            response = yout[0]
        else:
            tout, response = signal.step(
                (numerator, denominator),
                T=t_values,
            )
    except Exception as error:
        raise MathToolRuntimeError(f"step: {error}") from error

    return np.asarray(tout).reshape(-1), np.squeeze(response)


def impulse_response(model, t=None):
    signal = require_scipy_signal()
    numerator, denominator, tf_model = transfer_coefficients(model, "impulse")
    t_values = None if t is None else time_vector(t, "impulse")

    try:
        if tf_model.is_discrete:
            system = signal.dlti(numerator, denominator, dt=tf_model.Ts)
            tout, yout = signal.dimpulse(system, t=t_values)
            response = yout[0]
        else:
            tout, response = signal.impulse(
                (numerator, denominator),
                T=t_values,
            )
    except Exception as error:
        raise MathToolRuntimeError(f"impulse: {error}") from error

    return np.asarray(tout).reshape(-1), np.squeeze(response)


def bode_response(model, w=None):
    if isinstance(model, FrequencyResponseModel):
        frequency = model.frequencies
        response = np.asarray(model.response).reshape(-1)

        if w is not None:
            requested = frequency_vector(w, "bode")
            real_response = np.interp(
                requested,
                np.real(frequency),
                np.real(response),
            )
            imag_response = np.interp(
                requested,
                np.real(frequency),
                np.imag(response),
            )
            frequency = requested
            response = real_response + 1j * imag_response

        magnitude_db = 20 * np.log10(np.abs(response))
        phase_deg = np.rad2deg(np.unwrap(np.angle(response)))
        return (
            np.asarray(frequency, dtype=float).reshape(-1),
            magnitude_db.reshape(-1),
            phase_deg.reshape(-1),
        )

    signal = require_scipy_signal()
    numerator, denominator, tf_model = transfer_coefficients(model, "bode")
    frequencies = None if w is None else frequency_vector(w, "bode")

    try:
        if tf_model.is_discrete:
            system = signal.dlti(numerator, denominator, dt=tf_model.Ts)
            result = signal.dbode(system, w=frequencies)
        else:
            result = signal.bode(
                (numerator, denominator),
                w=frequencies,
            )
    except Exception as error:
        raise MathToolRuntimeError(f"bode: {error}") from error

    frequency, magnitude_db, phase_deg = result
    return (
        np.asarray(frequency).reshape(-1),
        np.asarray(magnitude_db).reshape(-1),
        np.asarray(phase_deg).reshape(-1),
    )


def frequency_response(model, w):
    if isinstance(model, FrequencyResponseModel):
        requested = frequency_vector(w, "freqresp")
        response = np.asarray(model.response).reshape(-1)
        real_response = np.interp(
            requested,
            np.real(model.frequencies),
            np.real(response),
        )
        imag_response = np.interp(
            requested,
            np.real(model.frequencies),
            np.imag(response),
        )
        return real_response + 1j * imag_response

    numerator, denominator, _ = transfer_coefficients(model, "freqresp")
    frequencies = frequency_vector(w, "freqresp")
    s = 1j * frequencies

    return np.polyval(numerator, s) / np.polyval(denominator, s)


def initial_response(model, x0, t=None):
    signal = require_scipy_signal()
    ss_model = to_state_space_checked(model, "initial")
    initial_state = np.asarray(x0, dtype=float).reshape(-1)

    if initial_state.size != ss_model.A.shape[0]:
        raise MathToolRuntimeError(
            "initial: x0 length must match number of states"
        )

    if t is None:
        t_values = (
            np.arange(0, 100) * ss_model.Ts
            if ss_model.is_discrete
            else np.linspace(0, 5, 100)
        )
    else:
        t_values = time_vector(t, "initial")

    try:
        if ss_model.is_discrete:
            tout, yout, _ = signal.dlsim(
                (ss_model.A, ss_model.B, ss_model.C, ss_model.D, ss_model.Ts),
                np.zeros((len(t_values), ss_model.B.shape[1])),
                t=t_values,
                x0=initial_state,
            )
        else:
            tout, yout, _ = signal.lsim(
                (ss_model.A, ss_model.B, ss_model.C, ss_model.D),
                U=np.zeros((len(t_values), ss_model.B.shape[1]))
                if t_values is not None
                else None,
                T=t_values,
                X0=initial_state,
            )
    except Exception as error:
        raise MathToolRuntimeError(f"initial: {error}") from error

    return np.asarray(tout).reshape(-1), np.squeeze(yout)


def lsim_response(model, u, t):
    signal = require_scipy_signal()
    ss_model = to_state_space_checked(model, "lsim")
    t_values = time_vector(t, "lsim")
    input_values = np.asarray(u, dtype=float)

    if input_values.ndim == 1:
        input_values = input_values.reshape(-1, 1)

    if input_values.shape[0] != t_values.size:
        raise MathToolRuntimeError(
            "lsim: input row count must match time vector length"
        )

    if input_values.shape[1] != ss_model.B.shape[1]:
        raise MathToolRuntimeError(
            "lsim: input column count must match system inputs"
        )

    try:
        if ss_model.is_discrete:
            tout, yout, _ = signal.dlsim(
                (ss_model.A, ss_model.B, ss_model.C, ss_model.D, ss_model.Ts),
                input_values,
                t=t_values,
            )
        else:
            tout, yout, _ = signal.lsim(
                (ss_model.A, ss_model.B, ss_model.C, ss_model.D),
                U=input_values,
                T=t_values,
            )
    except Exception as error:
        raise MathToolRuntimeError(f"lsim: {error}") from error

    return np.asarray(tout).reshape(-1), np.squeeze(yout)


def step_info(model, t=None):
    time, response = step_response(model, t)
    y = np.asarray(response, dtype=float).reshape(-1)
    final = y[-1] if y.size else np.nan

    if np.isclose(final, 0):
        target_low = target_high = np.nan
    else:
        target_low = 0.1 * final
        target_high = 0.9 * final

    rise_time = np.nan
    if y.size and not np.isnan(target_low):
        try:
            start_index = np.flatnonzero(y >= target_low)[0]
            end_index = np.flatnonzero(y >= target_high)[0]
            rise_time = time[end_index] - time[start_index]
        except IndexError:
            pass

    settling_time = np.nan
    if y.size and not np.isclose(final, 0):
        band = 0.02 * abs(final)
        outside = np.flatnonzero(np.abs(y - final) > band)
        if outside.size:
            index = min(outside[-1] + 1, time.size - 1)
            settling_time = time[index]
        else:
            settling_time = time[0]

    peak_index = int(np.argmax(np.abs(y))) if y.size else 0
    peak = y[peak_index] if y.size else np.nan
    peak_time = time[peak_index] if y.size else np.nan
    overshoot = (
        max(0.0, (np.max(y) - final) / abs(final) * 100)
        if y.size and not np.isclose(final, 0)
        else np.nan
    )
    undershoot = (
        max(0.0, -np.min(y) / abs(final) * 100)
        if y.size and not np.isclose(final, 0)
        else np.nan
    )

    return {
        "RiseTime": float(np.real_if_close(rise_time)),
        "SettlingTime": float(np.real_if_close(settling_time)),
        "SettlingMin": float(np.min(y)) if y.size else np.nan,
        "SettlingMax": float(np.max(y)) if y.size else np.nan,
        "Overshoot": float(np.real_if_close(overshoot)),
        "Undershoot": float(np.real_if_close(undershoot)),
        "Peak": float(np.real_if_close(peak)),
        "PeakTime": float(np.real_if_close(peak_time)),
    }


def bandwidth(model):
    frequency, magnitude_db, _ = bode_response(model)
    if magnitude_db.size == 0:
        return np.nan

    threshold = magnitude_db[0] - 3.0
    below = np.flatnonzero(magnitude_db <= threshold)

    if below.size == 0:
        return np.nan

    return float(frequency[below[0]])


def to_state_space_checked(model, function_name):
    require_lti_model(model, function_name)
    return to_state_space(model)
