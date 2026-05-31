import numpy as np


def finite_difference_gradient(fun, x, step_size=1e-6, method="2-point"):
    x = np.asarray(x, dtype=float).reshape(-1)
    gradient = np.zeros_like(x)

    if method == "3-point":
        for index in range(x.size):
            step = step_size * max(1.0, abs(x[index]))
            forward = x.copy()
            backward = x.copy()
            forward[index] += step
            backward[index] -= step
            gradient[index] = (fun(forward) - fun(backward)) / (2.0 * step)
        return gradient

    f0 = fun(x)
    for index in range(x.size):
        step = step_size * max(1.0, abs(x[index]))
        forward = x.copy()
        forward[index] += step
        gradient[index] = (fun(forward) - f0) / step

    return gradient
