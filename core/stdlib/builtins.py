import math
import numpy as np


def builtin_print(*args):
    print(*args)
    return None


def builtin_println(*args):
    print(*args)
    return None


def builtin_sin(x):
    return np.sin(x)


def builtin_cos(x):
    return np.cos(x)


def builtin_tan(x):
    return np.tan(x)


def builtin_sqrt(x):
    return np.sqrt(x)


def builtin_abs(x):
    return np.abs(x)


def builtin_zeros(n):
    return np.zeros(int(n))


def builtin_ones(n):
    return np.ones(int(n))


def builtin_length(x):
    return len(x)


BUILTIN_FUNCTIONS = {
    "print": builtin_print,
    "println": builtin_println,

    "sin": builtin_sin,
    "cos": builtin_cos,
    "tan": builtin_tan,

    "sqrt": builtin_sqrt,
    "abs": builtin_abs,

    "zeros": builtin_zeros,
    "ones": builtin_ones,

    "length": builtin_length,
}