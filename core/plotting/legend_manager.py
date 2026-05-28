import numpy as np

from core.errors.errors import RuntimeError as MathToolRuntimeError


LEGEND_PROPERTIES = {
    "location": "Location",
    "orientation": "Orientation",
    "fontsize": "FontSize",
    "textcolor": "TextColor",
    "box": "Box",
}


LOCATION_MAP = {
    "best": {"loc": "best"},
    "north": {"loc": "upper center"},
    "south": {"loc": "lower center"},
    "east": {"loc": "center right"},
    "west": {"loc": "center left"},
    "northeast": {"loc": "upper right"},
    "northwest": {"loc": "upper left"},
    "southeast": {"loc": "lower right"},
    "southwest": {"loc": "lower left"},
    "northoutside": {
        "loc": "lower center",
        "bbox_to_anchor": (0.5, 1.02),
    },
    "southoutside": {
        "loc": "upper center",
        "bbox_to_anchor": (0.5, -0.12),
    },
    "eastoutside": {
        "loc": "center left",
        "bbox_to_anchor": (1.02, 0.5),
    },
    "westoutside": {
        "loc": "center right",
        "bbox_to_anchor": (-0.02, 0.5),
    },
    "northeastoutside": {
        "loc": "upper left",
        "bbox_to_anchor": (1.02, 1),
    },
    "northwestoutside": {
        "loc": "upper right",
        "bbox_to_anchor": (-0.02, 1),
    },
    "southeastoutside": {
        "loc": "lower left",
        "bbox_to_anchor": (1.02, 0),
    },
    "southwestoutside": {
        "loc": "lower right",
        "bbox_to_anchor": (-0.02, 0),
    },
}


def parse_legend_arguments(arguments):
    if len(arguments) == 1 and isinstance(arguments[0], str):
        command = arguments[0].lower()

        if command in {"off", "show", "hide"}:
            return command, [], {}

    labels = []
    properties = {}
    index = 0

    while index < len(arguments):
        argument = arguments[index]

        if is_legend_property_name(argument):
            properties = parse_legend_properties(arguments[index:])
            break

        labels.extend(labels_from_argument(argument))
        index += 1

    return "create", labels, properties


def parse_legend_properties(arguments):
    if len(arguments) % 2 != 0:
        raise MathToolRuntimeError(
            f"legend: Missing value for property '{arguments[-1]}'"
        )

    properties = {}

    for index in range(0, len(arguments), 2):
        name = arguments[index]

        if not isinstance(name, str):
            raise MathToolRuntimeError(
                "legend: property names must be strings"
            )

        canonical = LEGEND_PROPERTIES.get(name.lower())

        if canonical is None:
            raise MathToolRuntimeError(
                f"legend: unknown property '{name}'"
            )

        properties[canonical] = normalize_legend_property(
            canonical,
            arguments[index + 1],
        )

    return properties


def labels_from_argument(value):
    if isinstance(value, str):
        return [value]

    try:
        array = np.asarray(value, dtype=object)
    except (TypeError, ValueError) as error:
        raise MathToolRuntimeError(
            "legend: labels must be strings"
        ) from error

    if array.size == 0:
        return []

    labels = []

    for item in array.reshape(-1, order="C"):
        if isinstance(item, np.generic):
            item = item.item()

        if not isinstance(item, str):
            raise MathToolRuntimeError(
                "legend: labels must be strings"
            )

        labels.append(item)

    return labels


def normalize_legend_property(name, value):
    if name == "Location":
        location = str(value).lower()

        if location not in LOCATION_MAP:
            raise MathToolRuntimeError(
                f"legend: unknown location '{value}'"
            )

        return location

    if name == "Orientation":
        orientation = str(value).lower()

        if orientation not in {"vertical", "horizontal"}:
            raise MathToolRuntimeError(
                f"legend: invalid orientation '{value}'"
            )

        return orientation

    if name == "FontSize":
        return float(value)

    if name == "TextColor":
        return str(value)

    if name == "Box":
        lowered = str(value).lower()

        if lowered in {"on", "true", "1"}:
            return True

        if lowered in {"off", "false", "0"}:
            return False

        return bool(value)

    return value


def legend_kwargs(properties, label_count):
    kwargs = dict(
        LOCATION_MAP.get(
            properties.get("Location", "best"),
            LOCATION_MAP["best"],
        )
    )

    if properties.get("Orientation") == "horizontal":
        kwargs["ncol"] = max(1, label_count)

    if "FontSize" in properties:
        kwargs["fontsize"] = properties["FontSize"]

    if "Box" in properties:
        kwargs["frameon"] = properties["Box"]

    return kwargs


def apply_legend_text_options(legend, properties):
    if legend is None or "TextColor" not in properties:
        return

    for text in legend.get_texts():
        text.set_color(properties["TextColor"])


def is_legend_property_name(value):
    return isinstance(value, str) and value.lower() in LEGEND_PROPERTIES
