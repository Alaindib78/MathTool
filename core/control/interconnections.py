from __future__ import annotations

from numbers import Number

import numpy as np

from core.control.conversions import require_lti_model, to_transfer_function
from core.control.conversions import to_state_space
from core.control.state_space import StateSpaceModel
from core.control.transfer_function import TransferFunctionModel
from core.errors.errors import RuntimeError as MathToolRuntimeError


def as_transfer_or_scalar(value, function_name):
    if isinstance(value, (Number, np.number)):
        return TransferFunctionModel([value], [1])

    require_lti_model(value, function_name)
    return to_transfer_function(value)


def series(sys1, sys2):
    return as_transfer_or_scalar(sys1, "series") * as_transfer_or_scalar(
        sys2,
        "series",
    )


def parallel(sys1, sys2):
    return as_transfer_or_scalar(sys1, "parallel") + as_transfer_or_scalar(
        sys2,
        "parallel",
    )


def feedback(sys1, sys2=1, sign=-1):
    forward = as_transfer_or_scalar(sys1, "feedback")
    feedback_path = as_transfer_or_scalar(sys2, "feedback")

    if sign not in {-1, 1, -1.0, 1.0}:
        raise MathToolRuntimeError(
            "feedback: sign must be +1 or -1"
        )

    n1 = forward.numerator
    d1 = forward.denominator
    n2 = feedback_path.numerator
    d2 = feedback_path.denominator
    numerator = np.convolve(n1, d2)
    open_loop_numerator = np.convolve(n1, n2)
    open_loop_denominator = np.convolve(d1, d2)

    if sign == -1:
        denominator = np.polyadd(open_loop_denominator, open_loop_numerator)
    else:
        denominator = np.polysub(open_loop_denominator, open_loop_numerator)

    return TransferFunctionModel(numerator, denominator, forward.Ts)


def append(*systems):
    if len(systems) < 2:
        raise MathToolRuntimeError(
            "append: expected at least two LTI models"
        )

    state_models = []
    for system in systems:
        require_lti_model(system, "append")
        state_models.append(to_state_space(system))

    try:
        from scipy import linalg
    except ImportError as error:
        raise MathToolRuntimeError(
            "append: scipy.linalg is required"
        ) from error

    sample_time = state_models[0].Ts
    if any(not np.isclose(model.Ts, sample_time) for model in state_models):
        raise MathToolRuntimeError(
            "append: sample times must match"
        )

    A = linalg.block_diag(*(model.A for model in state_models))
    B = linalg.block_diag(*(model.B for model in state_models))
    C = linalg.block_diag(*(model.C for model in state_models))
    D = linalg.block_diag(*(model.D for model in state_models))

    return StateSpaceModel(A, B, C, D, sample_time)
