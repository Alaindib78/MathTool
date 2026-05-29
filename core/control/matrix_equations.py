from __future__ import annotations

import numpy as np

from core.errors.errors import RuntimeError as MathToolRuntimeError


def scipy_linalg(function_name):
    try:
        from scipy import linalg
    except ImportError as error:
        raise MathToolRuntimeError(
            f"{function_name}: scipy.linalg is required"
        ) from error

    return linalg


def matrix(value, function_name, name):
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


def lyap(A, Q):
    linalg = scipy_linalg("lyap")
    return linalg.solve_continuous_lyapunov(
        matrix(A, "lyap", "A"),
        -matrix(Q, "lyap", "Q"),
    )


def dlyap(A, Q):
    linalg = scipy_linalg("dlyap")
    return linalg.solve_discrete_lyapunov(
        matrix(A, "dlyap", "A"),
        matrix(Q, "dlyap", "Q"),
    )


def care(A, B, Q, R):
    linalg = scipy_linalg("care")
    return linalg.solve_continuous_are(
        matrix(A, "care", "A"),
        matrix(B, "care", "B"),
        matrix(Q, "care", "Q"),
        matrix(R, "care", "R"),
    )


def dare(A, B, Q, R):
    linalg = scipy_linalg("dare")
    return linalg.solve_discrete_are(
        matrix(A, "dare", "A"),
        matrix(B, "dare", "B"),
        matrix(Q, "dare", "Q"),
        matrix(R, "dare", "R"),
    )
