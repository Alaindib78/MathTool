import numpy as np
from matplotlib.gridspec import GridSpec

from core.errors.errors import RuntimeError as MathToolRuntimeError


def parse_subplot_arguments(arguments):
    if len(arguments) >= 2 and str(arguments[0]).lower() == "position":
        if len(arguments) != 2:
            raise MathToolRuntimeError(
                "subplot: Position form expects one position vector"
            )

        return {
            "kind": "position",
            "position": position_vector(arguments[1]),
        }

    if len(arguments) < 3:
        raise MathToolRuntimeError(
            "subplot: expected m, n, and p"
        )

    rows = positive_integer(arguments[0], "m")
    columns = positive_integer(arguments[1], "n")
    indices = subplot_indices(arguments[2], rows, columns)
    options = parse_subplot_options(arguments[3:])

    return {
        "kind": "grid",
        "rows": rows,
        "columns": columns,
        "indices": indices,
        "replace": options["replace"],
    }


def select_subplot_axis(engine, figure, spec):
    if spec["kind"] == "position":
        axis = figure.add_axes(spec["position"])
        engine.set_current_axes(axis)
        return axis

    axes_for_figure = engine.subplot_axes_for_current_figure()
    key = (
        spec["rows"],
        spec["columns"],
        tuple(spec["indices"]),
    )

    if spec["replace"] and key in axes_for_figure:
        axes_for_figure[key].remove()
        del axes_for_figure[key]

    axis = axes_for_figure.get(key)

    if axis is not None and axis in figure.axes:
        engine.set_current_axes(axis)
        return axis

    axis = create_subplot_axis(figure, spec)
    axes_for_figure[key] = axis
    engine.set_current_axes(axis)
    return axis


def create_subplot_axis(figure, spec):
    indices = spec["indices"]

    if len(indices) == 1:
        return figure.add_subplot(
            spec["rows"],
            spec["columns"],
            indices[0],
        )

    rows = []
    columns = []

    for index in indices:
        zero_based = index - 1
        rows.append(zero_based // spec["columns"])
        columns.append(zero_based % spec["columns"])

    row_min, row_max = min(rows), max(rows)
    column_min, column_max = min(columns), max(columns)
    expected = {
        row * spec["columns"] + column + 1
        for row in range(row_min, row_max + 1)
        for column in range(column_min, column_max + 1)
    }

    if set(indices) != expected:
        raise MathToolRuntimeError(
            "subplot: vector p must define a rectangular span"
        )

    grid = GridSpec(spec["rows"], spec["columns"], figure=figure)

    return figure.add_subplot(
        grid[row_min:row_max + 1, column_min:column_max + 1]
    )


def positive_integer(value, name):
    if isinstance(value, np.generic):
        value = value.item()

    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise MathToolRuntimeError(
            f"subplot: {name} must be a positive integer"
        ) from error

    if not number.is_integer() or number < 1:
        raise MathToolRuntimeError(
            f"subplot: {name} must be a positive integer"
        )

    return int(number)


def subplot_indices(value, rows, columns):
    array = np.asarray(value)

    if array.ndim == 0:
        values = [array.item()]
    elif array.ndim <= 2 and 1 in array.shape:
        values = array.reshape(-1).tolist()
    else:
        raise MathToolRuntimeError(
            "subplot: p must be an index or vector of indices"
        )

    indices = [positive_integer(item, "p") for item in values]
    maximum = rows * columns

    for index in indices:
        if index < 1 or index > maximum:
            raise MathToolRuntimeError(
                "subplot: index p must be between 1 and m*n"
            )

    return indices


def position_vector(value):
    try:
        values = np.asarray(value, dtype=float).reshape(-1)
    except (TypeError, ValueError) as error:
        raise MathToolRuntimeError(
            "subplot: Position must be numeric"
        ) from error

    if values.size != 4:
        raise MathToolRuntimeError(
            "subplot: Position must have four elements"
        )

    return [float(item) for item in values]


def parse_subplot_options(arguments):
    options = {
        "replace": False,
    }

    for argument in arguments:
        if not isinstance(argument, str):
            raise MathToolRuntimeError(
                "subplot: options must be strings"
            )

        lowered = argument.lower()

        if lowered == "replace":
            options["replace"] = True
        elif lowered == "align":
            pass
        else:
            raise MathToolRuntimeError(
                f"subplot: unknown option '{argument}'"
            )

    return options
