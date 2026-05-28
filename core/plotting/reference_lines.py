import numpy as np

from core.errors.errors import RuntimeError as MathToolRuntimeError
from core.plotting.line_spec import (
    is_known_property_name,
    matplotlib_kwargs,
    normalize_color,
    parse_line_spec,
)
from core.plotting.tick_manager import numeric_vector


REFERENCE_LINE_PROPERTIES = {
    "color": "Color",
    "alpha": "Alpha",
    "linewidth": "LineWidth",
    "displayname": "DisplayName",
    "labelhorizontalalignment": "LabelHorizontalAlignment",
    "labelverticalalignment": "LabelVerticalAlignment",
    "labelorientation": "LabelOrientation",
}


def parse_reference_line_arguments(arguments, function_name):
    if not arguments:
        raise MathToolRuntimeError(
            f"{function_name}: expected coordinate argument"
        )

    coordinates = numeric_vector(
        arguments[0],
        function_name,
        "coordinates",
    )
    rest = list(arguments[1:])
    style = {}
    labels = None

    if rest and isinstance(rest[0], str):
        first = rest[0]

        if is_reference_property_name(first):
            pass
        else:
            try:
                style = parse_line_spec(
                    first,
                    function_name,
                    allow_markers=False,
                ).merged_properties()
                rest.pop(0)
            except MathToolRuntimeError:
                if looks_like_line_spec(first):
                    raise

                if len(rest) == 1 or (
                    len(rest) > 1 and is_reference_property_name(rest[1])
                ):
                    labels = labels_from_value(first, function_name)
                    rest.pop(0)
                else:
                    raise

    if labels is None and rest:
        if not is_reference_property_name(rest[0]):
            labels = labels_from_value(rest.pop(0), function_name)

    properties = parse_reference_name_value_pairs(rest, function_name)
    style.update(properties)
    validate_label_count(labels, coordinates.size, function_name)

    return coordinates, style, labels


def labels_from_value(value, function_name):
    if isinstance(value, str):
        return [value]

    try:
        array = np.asarray(value, dtype=object)
    except (TypeError, ValueError) as error:
        raise MathToolRuntimeError(
            f"{function_name}: labels must be strings"
        ) from error

    if array.size == 0:
        return []

    labels = []

    for item in array.reshape(-1, order="C"):
        if isinstance(item, np.generic):
            item = item.item()

        if not isinstance(item, str):
            raise MathToolRuntimeError(
                f"{function_name}: labels must be strings"
            )

        labels.append(item)

    return labels


def validate_label_count(labels, coordinate_count, function_name):
    if labels is None or len(labels) in {0, 1, coordinate_count}:
        return

    raise MathToolRuntimeError(
        f"{function_name}: number of labels must match number of lines"
    )


def parse_reference_name_value_pairs(arguments, function_name):
    if len(arguments) % 2 != 0:
        raise MathToolRuntimeError(
            f"{function_name}: Missing value for property '{arguments[-1]}'"
        )

    properties = {}

    for index in range(0, len(arguments), 2):
        name = arguments[index]

        if not isinstance(name, str):
            raise MathToolRuntimeError(
                f"{function_name}: property names must be strings"
            )

        canonical = REFERENCE_LINE_PROPERTIES.get(name.lower())

        if canonical is None:
            if is_known_property_name(name):
                canonical = {
                    "LineStyle": "LineStyle",
                    "linestyle": "LineStyle",
                }.get(name.lower())

            if canonical is None:
                raise MathToolRuntimeError(
                    f"{function_name}: unknown property '{name}'"
                )

        properties[canonical] = normalize_reference_property(
            canonical,
            arguments[index + 1],
            function_name,
        )

    return properties


def normalize_reference_property(name, value, function_name):
    if name == "Color":
        return normalize_color(value)

    if name in {"LineWidth", "Alpha"}:
        return float(value)

    if name in {
        "DisplayName",
        "LabelHorizontalAlignment",
        "LabelVerticalAlignment",
        "LabelOrientation",
    }:
        return str(value)

    if name == "LineStyle":
        return parse_line_spec(
            str(value),
            function_name,
            allow_markers=False,
        ).line_style

    raise MathToolRuntimeError(
        f"{function_name}: unknown property '{name}'"
    )


def reference_line_kwargs(properties):
    kwargs = matplotlib_kwargs(properties)

    if "Alpha" in properties:
        kwargs["alpha"] = properties["Alpha"]

    if "DisplayName" in properties:
        kwargs["label"] = properties["DisplayName"]

    return kwargs


def text_alignment(properties, orientation):
    horizontal = properties.get("LabelHorizontalAlignment")
    vertical = properties.get("LabelVerticalAlignment")

    if horizontal is None:
        horizontal = "left" if orientation == "x" else "center"

    if vertical is None:
        vertical = "top" if orientation == "x" else "bottom"

    return horizontal, vertical


def text_rotation(properties, orientation):
    requested = str(
        properties.get("LabelOrientation", "")
    ).lower()

    if requested == "horizontal":
        return 0

    if requested == "aligned":
        return 90 if orientation == "x" else 0

    return 90 if orientation == "x" else 0


def label_for_index(labels, index):
    if labels is None or not labels:
        return None

    if len(labels) == 1:
        return labels[0]

    return labels[index]


def is_reference_property_name(value):
    return (
        isinstance(value, str)
        and value.lower() in REFERENCE_LINE_PROPERTIES
    )


def looks_like_line_spec(value):
    return any(token in value for token in ("-", ":", ".")) or value in {
        "r",
        "g",
        "b",
        "c",
        "m",
        "y",
        "k",
        "w",
    }
