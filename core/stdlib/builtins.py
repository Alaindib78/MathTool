import math
import numpy as np


def builtin_print(context,*args):
    print(*args)
    return None


def builtin_println(context,*args):
    print(*args)
    return None


def builtin_sin(context,x):
    return np.sin(x)


def builtin_cos(context,x):
    return np.cos(x)


def builtin_tan(context,x):
    return np.tan(x)


def builtin_sqrt(context,x):
    return np.sqrt(x)


def builtin_abs(context,x):
    return np.abs(x)


def builtin_zeros(context,n):
    return np.zeros(int(n))


def builtin_ones(context,n):
    return np.ones(int(n))


def builtin_length(context,x):
    return len(x)

def builtin_plot(context, x, y):
    context.plot_engine.plot(x, y)


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

    "sqrt": builtin_sqrt,
    "abs": builtin_abs,

    "zeros": builtin_zeros,
    "ones": builtin_ones,

    "length": builtin_length,
    "plot": builtin_plot,
    "title": builtin_title,
    "xlabel": builtin_xlabel,
    "ylabel": builtin_ylabel,
    "grid": builtin_grid,
}