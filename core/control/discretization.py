from __future__ import annotations

import numpy as np

from core.control.conversions import require_lti_model, require_scipy_signal, to_state_space
from core.control.lti import validate_sample_time
from core.control.state_space import StateSpaceModel
from core.control.transfer_function import TransferFunctionModel
from core.errors.errors import RuntimeError as MathToolRuntimeError


METHOD_MAP = {
    "zoh": "zoh",
    "foh": "foh",
    "tustin": "bilinear",
    "bilinear": "bilinear",
}


def c2d(model, Ts, method="zoh"):
    require_lti_model(model, "c2d")
    sample_time = validate_sample_time(Ts, "c2d")

    if sample_time <= 0:
        raise MathToolRuntimeError("c2d: Ts must be positive")

    if model.is_discrete:
        raise MathToolRuntimeError("c2d: system is already discrete")

    method_key = str(method).lower()

    if method_key not in METHOD_MAP:
        raise MathToolRuntimeError(
            f"c2d: unsupported method '{method}'"
        )

    signal = require_scipy_signal()
    ss = to_state_space(model)

    try:
        A, B, C, D, dt = signal.cont2discrete(
            (ss.A, ss.B, ss.C, ss.D),
            sample_time,
            method=METHOD_MAP[method_key],
        )
    except Exception as error:
        raise MathToolRuntimeError(f"c2d: {error}") from error

    return StateSpaceModel(A, B, C, D, dt)


def d2c(model, method="zoh"):
    require_lti_model(model, "d2c")
    raise MathToolRuntimeError(
        "d2c: continuous conversion is not implemented yet"
    )


def is_discrete_time(model):
    require_lti_model(model, "isdt")
    return bool(model.is_discrete)


def is_continuous_time(model):
    require_lti_model(model, "isct")
    return not bool(model.is_discrete)
