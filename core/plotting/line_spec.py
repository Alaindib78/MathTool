from dataclasses import dataclass, field

import numpy as np

from core.errors.errors import RuntimeError as MathToolRuntimeError


LINE_STYLES = {
    "-",
    "--",
    ":",
    "-.",
}

MARKERS = {
    "o",
    "+",
    "*",
    ".",
    "x",
    "s",
    "d",
    "^",
    "v",
    ">",
    "<",
    "p",
    "h",
}

SHORT_COLORS = {
    "r": "r",
    "g": "g",
    "b": "b",
    "c": "c",
    "m": "m",
    "y": "y",
    "k": "k",
    "w": "w",
}

COLOR_NAMES = {
    "red": "red",
    "green": "green",
    "blue": "blue",
    "cyan": "cyan",
    "magenta": "magenta",
    "yellow": "yellow",
    "black": "black",
    "white": "white",
}

PROPERTY_NAMES = {
    "color": "Color",
    "linestyle": "LineStyle",
    "linewidth": "LineWidth",
    "marker": "Marker",
    "markersize": "MarkerSize",
    "markeredgecolor": "MarkerEdgeColor",
    "markerfacecolor": "MarkerFaceColor",
    "markerindices": "MarkerIndices",
}


@dataclass
class LineStyleSpec:
    line_style: str | None = None
    marker: str | None = None
    color: object | None = None
    properties: dict = field(default_factory=dict)

    def merged_properties(self):
        properties = dict(self.properties)

        if self.line_style is not None:
            properties["LineStyle"] = self.line_style

        if self.marker is not None:
            properties["Marker"] = self.marker

        if self.color is not None:
            properties["Color"] = self.color

        return properties


def is_known_property_name(value):
    return isinstance(value, str) and value.lower() in PROPERTY_NAMES


def parse_line_spec(spec):
    if not isinstance(spec, str) or spec == "":
        raise MathToolRuntimeError(
            f"plot: Invalid LineSpec '{spec}'"
        )

    line_style = None
    marker = None
    color = None
    index = 0

    while index < len(spec):
        token = None

        for candidate in ("--", "-.", "-", ":"):
            if spec.startswith(candidate, index):
                token = candidate
                break

        if token is not None:
            if line_style is not None:
                raise invalid_line_spec(spec)

            line_style = token
            index += len(token)
            continue

        char = spec[index]

        if char in MARKERS:
            if marker is not None:
                raise invalid_line_spec(spec)

            marker = char
            index += 1
            continue

        if char in SHORT_COLORS:
            if color is not None:
                raise invalid_line_spec(spec)

            color = SHORT_COLORS[char]
            index += 1
            continue

        raise invalid_line_spec(spec)

    if line_style is None and marker is not None:
        line_style = "none"

    return LineStyleSpec(
        line_style=line_style,
        marker=marker,
        color=color,
    )


def normalize_properties(raw_properties):
    properties = {}

    for name, value in raw_properties.items():
        canonical = PROPERTY_NAMES.get(str(name).lower())

        if canonical is None:
            raise MathToolRuntimeError(
                f"plot: Unknown property '{name}'"
            )

        properties[canonical] = normalize_property_value(
            canonical,
            value,
        )

    return properties


def normalize_property_value(name, value):
    if name in {
        "Color",
        "MarkerEdgeColor",
        "MarkerFaceColor",
    }:
        return normalize_color(value)

    if name == "LineStyle":
        return normalize_line_style(value)

    if name == "Marker":
        return normalize_marker(value)

    if name in {"LineWidth", "MarkerSize"}:
        return float(value)

    if name == "MarkerIndices":
        return normalize_marker_indices(value)

    return value


def normalize_color(value):
    if isinstance(value, np.generic):
        value = value.item()

    if isinstance(value, str):
        lowered = value.lower()

        if lowered in SHORT_COLORS:
            return SHORT_COLORS[lowered]

        if lowered in COLOR_NAMES:
            return COLOR_NAMES[lowered]

        raise MathToolRuntimeError(
            f"plot: Invalid color '{value}'"
        )

    array = np.asarray(value, dtype=float)

    if array.size != 3:
        raise MathToolRuntimeError(
            "plot: RGB color must have exactly three elements"
        )

    rgb = tuple(float(component) for component in array.reshape(-1))

    if any(component < 0 or component > 1 for component in rgb):
        raise MathToolRuntimeError(
            "plot: RGB color components must be between 0 and 1"
        )

    return rgb


def normalize_line_style(value):
    if isinstance(value, np.generic):
        value = value.item()

    text = str(value)

    if text == "none":
        return "none"

    if text not in LINE_STYLES:
        raise MathToolRuntimeError(
            f"plot: Invalid line style '{value}'"
        )

    return text


def normalize_marker(value):
    if isinstance(value, np.generic):
        value = value.item()

    text = str(value)

    if text == "none":
        return "none"

    if text not in MARKERS:
        raise MathToolRuntimeError(
            f"plot: Invalid marker '{value}'"
        )

    return text


def normalize_marker_indices(value):
    values = np.asarray(value).reshape(-1)
    indices = []

    for raw_index in values:
        if isinstance(raw_index, np.generic):
            raw_index = raw_index.item()

        numeric_index = float(raw_index)

        if not numeric_index.is_integer() or numeric_index < 1:
            raise MathToolRuntimeError(
                "plot: MarkerIndices must contain positive integers"
            )

        indices.append(int(numeric_index) - 1)

    return indices


def matplotlib_kwargs(properties):
    mapping = {
        "Color": "color",
        "LineStyle": "linestyle",
        "LineWidth": "linewidth",
        "Marker": "marker",
        "MarkerSize": "markersize",
        "MarkerEdgeColor": "markeredgecolor",
        "MarkerFaceColor": "markerfacecolor",
        "MarkerIndices": "markevery",
    }

    return {
        mapping[name]: value
        for name, value in properties.items()
        if name in mapping
    }


def invalid_line_spec(spec):
    return MathToolRuntimeError(
        f"plot: Invalid LineSpec '{spec}'"
    )
