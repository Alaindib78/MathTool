from __future__ import annotations

import numpy as np

from core.control.matrix_equations import care, dare, matrix
from core.control.transfer_function import TransferFunctionModel
from core.errors.errors import RuntimeError as MathToolRuntimeError


def place(A, B, desired_poles):
    try:
        from scipy import signal
    except ImportError as error:
        raise MathToolRuntimeError(
            "place: scipy.signal is required"
        ) from error

    result = signal.place_poles(
        matrix(A, "place", "A"),
        matrix(B, "place", "B"),
        np.asarray(desired_poles, dtype=complex).reshape(-1),
    )
    return result.gain_matrix


def acker(A, B, desired_poles):
    return place(A, B, desired_poles)


def lqr(A, B, Q, R):
    A = matrix(A, "lqr", "A")
    B = matrix(B, "lqr", "B")
    R = matrix(R, "lqr", "R")
    S = care(A, B, Q, R)
    K = np.linalg.solve(R, B.T @ S)
    poles = np.linalg.eigvals(A - B @ K)

    return {
        "K": np.real_if_close(K),
        "S": np.real_if_close(S),
        "P": poles,
    }


def dlqr(A, B, Q, R):
    A = matrix(A, "dlqr", "A")
    B = matrix(B, "dlqr", "B")
    R = matrix(R, "dlqr", "R")
    S = dare(A, B, Q, R)
    K = np.linalg.solve(B.T @ S @ B + R, B.T @ S @ A)
    poles = np.linalg.eigvals(A - B @ K)

    return {
        "K": np.real_if_close(K),
        "S": np.real_if_close(S),
        "P": poles,
    }


def pid(Kp, Ki=0.0, Kd=0.0):
    Kp = float(Kp)
    Ki = float(Ki)
    Kd = float(Kd)

    if np.isclose(Ki, 0) and np.isclose(Kd, 0):
        return TransferFunctionModel([Kp], [1])

    return TransferFunctionModel([Kd, Kp, Ki], [1, 0])
