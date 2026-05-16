import math
from pydoc import text
import numpy as np


def builtin_print(context,*args):
    text = " ".join(
        str(arg)
        for arg in args
    )

    if context.output_callback:
        context.output_callback(text)
    else:
        print(text)
    return None


def builtin_println(context,*args):
    text = " ".join(
        str(arg)
        for arg in args
    )

    if context.output_callback:
        context.output_callback(text)
    else:
        print(text)
    return None


def builtin_sin(context,x):
    return np.sin(x)


def builtin_cos(context,x):
    return np.cos(x)


def builtin_tan(context,x):
    return np.tan(x)

def builtin_asin(context,x):
    return np.arcsin(x)


def builtin_acos(context,x):
    return np.arccos(x)


def builtin_atan(context,x):
    return np.arctan(x)

def builtin_log(context,x):
    return np.log(x)

def builtin_log10(context,x):
    return np.log10(x)


def builtin_sqrt(context,x):
    return np.sqrt(x)


def builtin_abs(context,x):
    return np.abs(x)

def builtin_floor(context,x):
    return np.floor(x)

def builtin_ceil(context,x):
    return np.ceil(x)

def builtin_round(context,x):
    return np.round(x)

def builtin_sign(context,x):
    return np.sign(x)   

def builtin_zeros(context,n):
    return np.zeros(int(n))


def builtin_ones(context,n):
    return np.ones(int(n))


def _as_array(value):
    return np.asarray(value)


def builtin_eye(context, rows, cols=None):
    rows = int(rows)

    if cols is None:
        return np.eye(rows)

    return np.eye(rows, int(cols))


def builtin_det(context, value):
    array = _as_array(value)

    try:
        return float(np.round(np.linalg.det(array), 12))
    except np.linalg.LinAlgError as error:
        raise Exception(str(error))


def builtin_inv(context, value):
    array = _as_array(value)

    try:
        return np.linalg.inv(array)
    except np.linalg.LinAlgError as error:
        raise Exception(str(error))


def builtin_size(context, value, dim=None):
    array = _as_array(value)

    if dim is not None:
        axis = int(dim) - 1

        if axis < 0:
            raise Exception("Dimension must be positive")

        if array.ndim == 0:
            return 1 if axis == 0 else 1

        if axis >= array.ndim:
            return 1

        return int(array.shape[axis])

    if array.ndim == 0:
        return np.array([1, 1])

    return np.array(array.shape)


def builtin_sum(context, value, dim=None):
    array = _as_array(value)

    if dim is None:
        return np.sum(array)

    return np.sum(array, axis=int(dim) - 1)


def builtin_mean(context, value, dim=None):
    array = _as_array(value)

    if dim is None:
        return np.mean(array)

    return np.mean(array, axis=int(dim) - 1)


def builtin_max(context, value, dim=None):
    array = _as_array(value)

    if dim is None:
        return np.max(array)

    return np.max(array, axis=int(dim) - 1)


def builtin_min(context, value, dim=None):
    array = _as_array(value)

    if dim is None:
        return np.min(array)

    return np.min(array, axis=int(dim) - 1)


def builtin_length(context,x):
    return len(x)

def builtin_plot(context, x, y):
    context.plot_engine.plot(x, y)

def builtin_mod(context, a, b):
    return np.mod(a, b)

def builtin_title(context, text):
    context.plot_engine.title(text)


def builtin_xlabel(context, text):
    context.plot_engine.xlabel(text)


def builtin_ylabel(context, text):
    context.plot_engine.ylabel(text)


def builtin_grid(context, value=True):
    if value:
        context.plot_engine.grid_on()
    else:
        context.plot_engine.grid_off()

BUILTIN_FUNCTIONS = {
    "print": builtin_print,
    "println": builtin_println,

    "sin": builtin_sin,
    "cos": builtin_cos,
    "tan": builtin_tan,

    "asin": builtin_sin,
    "acos": builtin_acos,
    "atan": builtin_atan,

    "log": builtin_log,
    "log10": builtin_log10,

    "sqrt": builtin_sqrt,
    "abs": builtin_abs,

    "floor": builtin_floor,
    "ceil": builtin_ceil,
    "round": builtin_round,
    "sign": builtin_sign,

    "zeros": builtin_zeros,
    "ones": builtin_ones,
    "eye": builtin_eye,
    "det": builtin_det,
    "inv": builtin_inv,
    "size": builtin_size,
    "sum": builtin_sum,
    "mean": builtin_mean,
    "max": builtin_max,
    "min": builtin_min,

    "length": builtin_length,
    "plot": builtin_plot,
    "mod": builtin_mod,
    "title": builtin_title,
    "xlabel": builtin_xlabel,
    "ylabel": builtin_ylabel,
    "grid": builtin_grid,
}
