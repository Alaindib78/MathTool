import numpy as np
from matplotlib.ticker import AutoLocator, ScalarFormatter

from core.errors.errors import RuntimeError as MathToolRuntimeError


def tick_values_from_argument(value, function_name):
    values = numeric_vector(value, function_name, "tick values")

    if values.size > 1 and np.any(np.diff(values) < 0):
        raise MathToolRuntimeError(
            f"{function_name}: tick values must be increasing"
        )

    return values


def tick_labels_from_arguments(arguments, function_name, tick_count=None):
    if len(arguments) == 1:
        labels = labels_from_value(arguments[0], function_name)
    else:
        labels = [
            label_from_value(argument, function_name)
            for argument in arguments
        ]

    if tick_count is not None and len(labels) < tick_count:
        labels = labels + [""] * (tick_count - len(labels))

    return labels


def labels_from_value(value, function_name):
    if is_empty(value):
        return []

    if isinstance(value, str):
        return [value]

    try:
        array = np.asarray(value, dtype=object)
    except (TypeError, ValueError) as error:
        raise MathToolRuntimeError(
            f"{function_name}: tick labels must be strings"
        ) from error

    if array.ndim == 0:
        return [label_from_value(array.item(), function_name)]

    return [
        label_from_value(item, function_name)
        for item in array.reshape(-1, order="C")
    ]


def label_from_value(value, function_name):
    if isinstance(value, np.generic):
        value = value.item()

    if isinstance(value, str):
        return value

    raise MathToolRuntimeError(
        f"{function_name}: tick labels must be strings"
    )


def numeric_vector(value, function_name, description):
    if is_empty(value):
        return np.array([], dtype=float)

    if isinstance(value, str):
        raise MathToolRuntimeError(
            f"{function_name}: {description} must be numeric"
        )

    try:
        array = np.asarray(value)
    except (TypeError, ValueError) as error:
        raise MathToolRuntimeError(
            f"{function_name}: {description} must be numeric"
        ) from error

    if not np.issubdtype(array.dtype, np.number):
        raise MathToolRuntimeError(
            f"{function_name}: {description} must be numeric"
        )

    if array.ndim > 2 or (array.ndim == 2 and 1 not in array.shape):
        raise MathToolRuntimeError(
            f"{function_name}: {description} must be a vector"
        )

    return np.real(array.reshape(-1)).astype(float)


def set_tick_mode(axis, dimension, mode):
    if mode == "auto":
        get_axis(axis, dimension).set_major_locator(AutoLocator())
        get_axis(axis, dimension).set_major_formatter(ScalarFormatter())
    elif mode == "manual":
        values = get_ticks(axis, dimension)
        set_ticks(axis, dimension, values)
    else:
        raise MathToolRuntimeError(
            f"{dimension}ticks: mode must be 'auto' or 'manual'"
        )

    setattr(axis, f"_mathtool_{dimension}tick_mode", mode)


def get_tick_mode(axis, dimension):
    return getattr(axis, f"_mathtool_{dimension}tick_mode", "auto")


def set_tick_label_mode(axis, dimension, mode):
    if mode == "auto":
        get_axis(axis, dimension).set_major_formatter(ScalarFormatter())
    elif mode == "manual":
        labels = get_ticklabels(axis, dimension)
        set_ticklabels(axis, dimension, labels)
    else:
        raise MathToolRuntimeError(
            f"{dimension}ticklabels: mode must be 'auto' or 'manual'"
        )

    setattr(axis, f"_mathtool_{dimension}ticklabel_mode", mode)


def get_tick_label_mode(axis, dimension):
    return getattr(axis, f"_mathtool_{dimension}ticklabel_mode", "auto")


def set_ticks(axis, dimension, values):
    if dimension == "x":
        axis.set_xticks(values)
    else:
        axis.set_yticks(values)

    setattr(axis, f"_mathtool_{dimension}tick_mode", "manual")


def get_ticks(axis, dimension):
    if dimension == "x":
        return np.asarray(axis.get_xticks(), dtype=float)

    return np.asarray(axis.get_yticks(), dtype=float)


def set_ticklabels(axis, dimension, labels):
    ticks = get_ticks(axis, dimension)
    set_ticks(axis, dimension, ticks)

    if len(labels) < len(ticks):
        labels = labels + [""] * (len(ticks) - len(labels))

    if dimension == "x":
        axis.set_xticklabels(labels)
    else:
        axis.set_yticklabels(labels)

    setattr(axis, f"_mathtool_{dimension}ticklabel_mode", "manual")
    setattr(axis, f"_mathtool_{dimension}tick_mode", "manual")


def get_ticklabels(axis, dimension):
    if dimension == "x":
        labels = axis.get_xticklabels()
    else:
        labels = axis.get_yticklabels()

    return [label.get_text() for label in labels]


def get_axis(axis, dimension):
    return axis.xaxis if dimension == "x" else axis.yaxis


def is_empty(value):
    if value is None:
        return False

    try:
        return np.asarray(value).size == 0
    except (TypeError, ValueError):
        return False
