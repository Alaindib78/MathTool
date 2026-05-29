from __future__ import annotations

import numpy as np

from core.control.analysis import is_stable
from core.control.conversions import require_lti_model, to_state_space
from core.errors.errors import RuntimeError as MathToolRuntimeError


def numeric_matrix(value, function_name, name):
    try:
        array = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as error:
        raise MathToolRuntimeError(
            f"{function_name}: {name} must be numeric"
        ) from error

    if array.ndim == 1:
        array = array.reshape(-1, 1)

    if array.ndim != 2:
        raise MathToolRuntimeError(
            f"{function_name}: {name} must be a matrix"
        )

    return array


def controllability_matrix(A_or_sys, B=None):
    if B is None:
        require_lti_model(A_or_sys, "ctrb")
        sys = to_state_space(A_or_sys)
        A = np.asarray(sys.A, dtype=float)
        B = np.asarray(sys.B, dtype=float)
    else:
        A = numeric_matrix(A_or_sys, "ctrb", "A")
        B = numeric_matrix(B, "ctrb", "B")

    if A.shape[0] != A.shape[1] or B.shape[0] != A.shape[0]:
        raise MathToolRuntimeError("ctrb: incompatible A and B dimensions")

    blocks = []
    power = np.eye(A.shape[0])

    for _ in range(A.shape[0]):
        blocks.append(power @ B)
        power = power @ A

    return np.hstack(blocks)


def observability_matrix(A_or_sys, C=None):
    if C is None:
        require_lti_model(A_or_sys, "obsv")
        sys = to_state_space(A_or_sys)
        A = np.asarray(sys.A, dtype=float)
        C = np.asarray(sys.C, dtype=float)
    else:
        A = numeric_matrix(A_or_sys, "obsv", "A")
        C = numeric_matrix(C, "obsv", "C")

    if A.shape[0] != A.shape[1] or C.shape[1] != A.shape[0]:
        raise MathToolRuntimeError("obsv: incompatible A and C dimensions")

    blocks = []
    power = np.eye(A.shape[0])

    for _ in range(A.shape[0]):
        blocks.append(C @ power)
        power = power @ A

    return np.vstack(blocks)


def gramian(sys, kind):
    require_lti_model(sys, "gram")
    ss = to_state_space(sys)

    if not is_stable(ss):
        raise MathToolRuntimeError(
            "gram: Gramians are defined only for stable systems"
        )

    try:
        from scipy import linalg
    except ImportError as error:
        raise MathToolRuntimeError(
            "gram: scipy.linalg is required"
        ) from error

    kind = str(kind).lower()

    if kind in {"c", "controllability"}:
        return linalg.solve_continuous_lyapunov(
            ss.A,
            -(ss.B @ ss.B.T),
        )

    if kind in {"o", "observability"}:
        return linalg.solve_continuous_lyapunov(
            ss.A.T,
            -(ss.C.T @ ss.C),
        )

    raise MathToolRuntimeError("gram: kind must be 'c' or 'o'")
