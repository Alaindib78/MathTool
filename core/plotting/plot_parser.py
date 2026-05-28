from dataclasses import dataclass, field

import numpy as np

from core.errors.errors import RuntimeError as MathToolRuntimeError
from core.runtime.symbolic import is_symbolic
from core.plotting.line_spec import (
    LineStyleSpec,
    is_known_property_name,
    normalize_properties,
    parse_line_spec,
)


@dataclass
class PlotSeries:
    x: np.ndarray
    y: np.ndarray
    properties: dict = field(default_factory=dict)


def parse_plot_arguments(arguments):
    if not arguments:
        raise MathToolRuntimeError(
            "plot: expected at least one data argument"
        )

    data_arguments, properties = split_name_value_arguments(
        list(arguments)
    )

    if not data_arguments:
        raise MathToolRuntimeError(
            "plot: expected data before name-value properties"
        )

    series = parse_data_arguments(data_arguments)

    for item in series:
        item.properties.update(properties)

    return series


def split_name_value_arguments(arguments):
    for index, argument in enumerate(arguments):
        if is_known_property_name(argument):
            return (
                arguments[:index],
                parse_name_value_pairs(arguments[index:]),
            )

    for index, argument in enumerate(arguments[:-1]):
        if isinstance(argument, str):
            try:
                parse_line_spec(argument)
            except MathToolRuntimeError:
                raise MathToolRuntimeError(
                    f"plot: Unknown property '{argument}'"
                )

    return arguments, {}


def parse_name_value_pairs(arguments):
    if len(arguments) % 2 != 0:
        name = arguments[-1]

        raise MathToolRuntimeError(
            f"plot: Missing value for property '{name}'"
        )

    properties = {}

    for index in range(0, len(arguments), 2):
        name = arguments[index]

        if not isinstance(name, str):
            raise MathToolRuntimeError(
                "plot: property names must be strings"
            )

        if not is_known_property_name(name):
            raise MathToolRuntimeError(
                f"plot: Unknown property '{name}'"
            )

        properties[name] = arguments[index + 1]

    return normalize_properties(properties)


def parse_data_arguments(arguments):
    if is_single_implicit_group(arguments):
        y = arguments[0]
        style = optional_line_spec(arguments, 1)
        return implicit_x_series(y, style)

    series = []
    index = 0

    while index < len(arguments):
        if index + 1 >= len(arguments):
            raise MathToolRuntimeError(
                "plot: invalid plot argument count"
            )

        x = arguments[index]
        y = arguments[index + 1]
        index += 2

        style = LineStyleSpec()

        if index < len(arguments) and isinstance(arguments[index], str):
            style = parse_line_spec(arguments[index])
            index += 1

        series.extend(x_y_series(x, y, style))

    return series


def is_single_implicit_group(arguments):
    return (
        len(arguments) == 1
        or (
            len(arguments) == 2
            and isinstance(arguments[1], str)
        )
    )


def optional_line_spec(arguments, index):
    if index >= len(arguments):
        return LineStyleSpec()

    return parse_line_spec(arguments[index])


def implicit_x_series(y, style):
    y_array = numeric_array(y, "Y")

    if y_array.ndim == 0:
        return [
            PlotSeries(
                np.array([1.0]),
                np.array([float(np.real(y_array.item()))]),
                style.merged_properties(),
            )
        ]

    if is_vector(y_array):
        y_values = vector_values(y_array)
        x_values = np.arange(1, y_values.size + 1)

        return [
            PlotSeries(
                x_values,
                y_values,
                style.merged_properties(),
            )
        ]

    if y_array.ndim == 2:
        return [
            PlotSeries(
                np.arange(1, y_array.shape[0] + 1),
                np.real(y_array[:, column]),
                style.merged_properties(),
            )
            for column in range(y_array.shape[1])
        ]

    raise MathToolRuntimeError(
        "plot: Y must be a scalar, vector, or 2-D matrix"
    )


def x_y_series(x, y, style):
    x_array = numeric_array(x, "X")
    y_array = numeric_array(y, "Y")

    if x_array.ndim == 0 and y_array.ndim == 0:
        return [
            PlotSeries(
                np.array([float(np.real(x_array.item()))]),
                np.array([float(np.real(y_array.item()))]),
                style.merged_properties(),
            )
        ]

    if is_vector(x_array) and is_vector(y_array):
        x_values = vector_values(x_array)
        y_values = vector_values(y_array)

        if x_values.size != y_values.size:
            raise MathToolRuntimeError(
                "plot: X and Y must have the same length"
            )

        return [
            PlotSeries(
                x_values,
                y_values,
                style.merged_properties(),
            )
        ]

    if x_array.ndim == 2 and y_array.ndim == 2:
        if x_array.shape != y_array.shape:
            raise MathToolRuntimeError(
                "plot: X and Y matrices must have the same shape"
            )

        return [
            PlotSeries(
                np.real(x_array[:, column]),
                np.real(y_array[:, column]),
                style.merged_properties(),
            )
            for column in range(x_array.shape[1])
        ]

    if is_vector(x_array) and y_array.ndim == 2:
        return vector_matrix_series(
            vector_values(x_array),
            y_array,
            style,
            vector_is_x=True,
        )

    if x_array.ndim == 2 and is_vector(y_array):
        return vector_matrix_series(
            vector_values(y_array),
            x_array,
            style,
            vector_is_x=False,
        )

    raise MathToolRuntimeError(
        "plot: invalid matrix dimensions"
    )


def vector_matrix_series(vector, matrix, style, *, vector_is_x):
    if vector.size == matrix.shape[0]:
        axis = "columns"
    elif vector.size == matrix.shape[1]:
        axis = "rows"
    else:
        raise MathToolRuntimeError(
            "plot: vector length must match a matrix dimension"
        )

    series = []

    if axis == "columns":
        for column in range(matrix.shape[1]):
            matrix_values = np.real(matrix[:, column])
            x_values = vector if vector_is_x else matrix_values
            y_values = matrix_values if vector_is_x else vector
            series.append(
                PlotSeries(
                    x_values,
                    y_values,
                    style.merged_properties(),
                )
            )
    else:
        for row in range(matrix.shape[0]):
            matrix_values = np.real(matrix[row, :])
            x_values = vector if vector_is_x else matrix_values
            y_values = matrix_values if vector_is_x else vector
            series.append(
                PlotSeries(
                    x_values,
                    y_values,
                    style.merged_properties(),
                )
            )

    return series


def numeric_array(value, name):
    if is_symbolic(value) or isinstance(value, str):
        raise MathToolRuntimeError(
            f"plot: {name} data must be numeric"
        )

    try:
        array = np.asarray(value)
    except (TypeError, ValueError) as error:
        raise MathToolRuntimeError(
            f"plot: {name} data must be numeric"
        ) from error

    if not np.issubdtype(array.dtype, np.number):
        raise MathToolRuntimeError(
            f"plot: {name} data must be numeric"
        )

    return array


def is_vector(array):
    return (
        array.ndim == 1
        or (
            array.ndim == 2
            and 1 in array.shape
        )
    )


def vector_values(array):
    return np.real(np.asarray(array).reshape(-1))
