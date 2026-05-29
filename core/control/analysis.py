from __future__ import annotations

import numpy as np

from core.control.conversions import (
    require_lti_model,
    to_transfer_function,
)
from core.control.lti import trim_leading_zeros
from core.control.state_space import StateSpaceModel
from core.control.transfer_function import TransferFunctionModel
from core.control.zero_pole_gain import ZeroPoleGainModel
from core.errors.errors import RuntimeError as MathToolRuntimeError


def poles(model):
    require_lti_model(model, "pole")

    if isinstance(model, StateSpaceModel):
        return np.linalg.eigvals(model.A)

    if isinstance(model, TransferFunctionModel):
        return np.roots(model.denominator)

    if isinstance(model, ZeroPoleGainModel):
        return model.poles

    return np.roots(to_transfer_function(model).denominator)


def zeros(model):
    require_lti_model(model, "zero")

    if isinstance(model, TransferFunctionModel):
        return np.roots(model.numerator)

    if isinstance(model, ZeroPoleGainModel):
        return model.zeros

    return np.roots(to_transfer_function(model).numerator)


def is_stable(model):
    system_poles = poles(model)

    if getattr(model, "is_discrete", False):
        return bool(np.all(np.abs(system_poles) < 1))

    return bool(np.all(np.real(system_poles) < 0))


def dc_gain(model):
    require_lti_model(model, "dcgain")

    if isinstance(model, StateSpaceModel):
        try:
            return np.real_if_close(
                model.D - model.C @ np.linalg.solve(model.A, model.B)
            )
        except np.linalg.LinAlgError as error:
            raise MathToolRuntimeError(
                "dcgain: A matrix is singular"
            ) from error

    tf_model = to_transfer_function(model)

    numerator = np.asarray(tf_model.numerator)
    denominator = np.asarray(tf_model.denominator)
    den0 = np.polyval(denominator, 0)

    if np.isclose(den0, 0):
        raise MathToolRuntimeError(
            "dcgain: denominator evaluates to zero at DC"
        )

    return np.real_if_close(np.polyval(numerator, 0) / den0).item()


def damping(model):
    system_poles = np.asarray(poles(model), dtype=complex)
    rows = []

    for pole_value in system_poles:
        if getattr(model, "is_discrete", False):
            if np.isclose(pole_value, 0):
                continuous_equivalent = complex(-np.inf)
            else:
                continuous_equivalent = np.log(pole_value) / model.Ts
            wn = abs(continuous_equivalent)
            zeta = (
                np.nan
                if not np.isfinite(wn) or np.isclose(wn, 0)
                else -continuous_equivalent.real / wn
            )
        else:
            wn = abs(pole_value)
            zeta = np.nan if np.isclose(wn, 0) else -pole_value.real / wn

        rows.append(
            {
                "Pole": pole_value,
                "Damping": float(np.real_if_close(zeta)),
                "Frequency": float(np.real_if_close(wn)),
            }
        )

    return rows


def minreal(model, tolerance=1e-6):
    require_lti_model(model, "minreal")
    tf_model = to_transfer_function(model)
    zeros_values = list(np.roots(tf_model.numerator))
    poles_values = list(np.roots(tf_model.denominator))
    remaining_zeros = []

    for zero_value in zeros_values:
        if poles_values:
            distances = np.abs(np.asarray(poles_values) - zero_value)
            index = int(np.argmin(distances))

            if distances[index] <= tolerance:
                poles_values.pop(index)
                continue

        remaining_zeros.append(zero_value)

    gain = tf_model.numerator[0] / tf_model.denominator[0]
    numerator = gain * np.poly(remaining_zeros)
    denominator = np.poly(poles_values)

    return TransferFunctionModel(
        trim_leading_zeros(numerator),
        trim_leading_zeros(denominator),
        tf_model.Ts,
    )
