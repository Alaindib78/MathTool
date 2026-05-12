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

    "length": builtin_length,
    "plot": builtin_plot,
    "mod": builtin_mod,
    "title": builtin_title,
    "xlabel": builtin_xlabel,
    "ylabel": builtin_ylabel,
    "grid": builtin_grid,
}