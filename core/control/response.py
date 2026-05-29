from __future__ import annotations

import numpy as np

from core.control.conversions import require_scipy_signal, to_transfer_function
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
