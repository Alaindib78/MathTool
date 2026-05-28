import math

import numpy as np

from core.errors.errors import RuntimeError as MathToolRuntimeError


AXIS_STYLES = {
    "tight",
    "padded",
    "tickaligned",
    "equal",
    "image",
    "square",
    "fill",
    "vis3d",
    "normal",
}

AXIS_DIRECTIONS = {
    "xy",
    "ij",
}


def apply_matplotlib_axis(axis, *arguments):
    if not arguments:
        return current_matplotlib_limits(axis), False

    if len(arguments) == 1 and is_visibility_argument(arguments[0]):
        set_matplotlib_visibility(axis, visibility_value(arguments[0]))
        return None, True

    if len(arguments) == 1 and not isinstance(arguments[0], str):
        set_matplotlib_limits(axis, axis_limit_vector(arguments[0]))
        return None, True

    if all(isinstance(argument, str) for argument in arguments):
        for command in axis_commands(arguments):
            apply_matplotlib_axis_command(axis, command)

        return None, True

    raise MathToolRuntimeError(
        "axis: expected limits vector or option string"
    )


def apply_recording_axis(engine, *arguments):
    if not arguments:
        return current_recording_limits(engine)

    if len(arguments) == 1 and is_visibility_argument(arguments[0]):
        set_recording_visibility(engine, visibility_value(arguments[0]))
        return None

    if len(arguments) == 1 and not isinstance(arguments[0], str):
        set_recording_limits(engine, axis_limit_vector(arguments[0]))
        return None

    if all(isinstance(argument, str) for argument in arguments):
        for command in axis_commands(arguments):
            apply_recording_axis_command(engine, command)

        return None

    raise MathToolRuntimeError(
        "axis: expected limits vector or option string"
    )


def axis_limit_vector(value):
    try:
        values = np.asarray(value, dtype=float).reshape(-1)
    except (TypeError, ValueError) as error:
        raise MathToolRuntimeError(
            "axis: limits must be numeric"
        ) from error

    if values.size not in {4, 6, 8}:
        raise MathToolRuntimeError(
            "axis: limits must have four, six, or eight elements"
        )

    for index in range(0, min(values.size, 6), 2):
        lower = values[index]
        upper = values[index + 1]

        if (
            math.isfinite(lower)
            and math.isfinite(upper)
            and lower >= upper
        ):
            raise MathToolRuntimeError(
                "axis: minimum limits must be less than maximum limits"
            )

    return values


def axis_commands(arguments):
    tokens = []

    for argument in arguments:
        tokens.extend(str(argument).lower().split())

    commands = []
    index = 0

    while index < len(tokens):
        token = tokens[index]

        if token == "auto" and index + 1 < len(tokens):
            candidate = f"auto {tokens[index + 1]}"

            if candidate in {
                "auto x",
                "auto y",
                "auto z",
                "auto xy",
                "auto xz",
                "auto yz",
            }:
                commands.append(candidate)
                index += 2
                continue

        if token in {
            "auto",
            "manual",
            "on",
            "off",
            *AXIS_STYLES,
            *AXIS_DIRECTIONS,
        }:
            commands.append(token)
            index += 1
            continue

        raise MathToolRuntimeError(
            f"axis: unknown option '{token}'"
        )

    return commands


def apply_matplotlib_axis_command(axis, command):
    if command == "on":
        axis.set_axis_on()
        return

    if command == "off":
        axis.set_axis_off()
        return

    if command == "manual":
        axis.set_autoscale_on(False)
        setattr(axis, "_mathtool_axis_mode", "manual")
        return

    if command == "auto":
        axis.set_autoscale_on(True)
        axis.relim()
        axis.autoscale_view()
        setattr(axis, "_mathtool_axis_mode", "auto")
        return

    if command.startswith("auto "):
        set_auto_axis(axis, command.removeprefix("auto "))
        setattr(axis, "_mathtool_axis_mode", "auto")
        return

    if command == "tight":
        axis.relim()
        axis.margins(0)
        axis.autoscale(enable=True, axis="both", tight=True)
        return

    if command == "padded":
        axis.relim()
        axis.margins(0.07)
        axis.autoscale(enable=True, axis="both", tight=False)
        return

    if command == "tickaligned":
        axis.relim()
        axis.autoscale(enable=True, axis="both", tight=False)
        return

    if command == "equal":
        axis.set_aspect("equal", adjustable="datalim")
        return

    if command == "image":
        axis.relim()
        axis.margins(0)
        axis.autoscale(enable=True, axis="both", tight=True)
        axis.set_aspect("equal", adjustable="box")
        return

    if command == "square":
        if hasattr(axis, "set_box_aspect"):
            axis.set_box_aspect(1)
        return

    if command in {"fill", "normal"}:
        axis.set_aspect("auto")

        if hasattr(axis, "set_box_aspect"):
            axis.set_box_aspect(None)

        return

    if command == "vis3d":
        if hasattr(axis, "set_box_aspect") and hasattr(
            axis,
            "get_box_aspect",
        ):
            axis.set_box_aspect(axis.get_box_aspect())

        return

    if command == "ij":
        if not axis.yaxis_inverted():
            axis.invert_yaxis()
        return

    if command == "xy":
        if axis.yaxis_inverted():
            axis.invert_yaxis()
        return

    raise MathToolRuntimeError(
        f"axis: unknown option '{command}'"
    )


def set_auto_axis(axis, axes):
    if "x" in axes:
        axis.autoscale(enable=True, axis="x")

    if "y" in axes:
        axis.autoscale(enable=True, axis="y")

    if "z" in axes and hasattr(axis, "autoscale"):
        axis.autoscale(enable=True, axis="z")

    axis.relim()
    axis.autoscale_view()


def set_matplotlib_limits(axis, limits):
    axis.relim()
    axis.autoscale_view()

    x_limits = resolve_pair(limits[0:2], axis.get_xlim())
    y_limits = resolve_pair(limits[2:4], axis.get_ylim())
    axis.set_xlim(x_limits)
    axis.set_ylim(y_limits)

    if limits.size >= 6 and hasattr(axis, "set_zlim"):
        z_limits = resolve_pair(limits[4:6], axis.get_zlim())
        axis.set_zlim(z_limits)

    if limits.size >= 8:
        apply_color_limits(axis, limits[6:8])

    setattr(axis, "_mathtool_axis_mode", "manual")


def resolve_pair(requested, automatic):
    lower = automatic[0] if math.isinf(requested[0]) else requested[0]
    upper = automatic[1] if math.isinf(requested[1]) else requested[1]

    if lower >= upper:
        raise MathToolRuntimeError(
            "axis: minimum limits must be less than maximum limits"
        )

    return float(lower), float(upper)


def apply_color_limits(axis, limits):
    for artist in [
        *getattr(axis, "images", []),
        *getattr(axis, "collections", []),
    ]:
        if hasattr(artist, "set_clim"):
            artist.set_clim(resolve_pair(limits, artist.get_clim()))


def current_matplotlib_limits(axis):
    values = [
        *axis.get_xlim(),
        *axis.get_ylim(),
    ]

    if hasattr(axis, "get_zlim"):
        values.extend(axis.get_zlim())

    return np.asarray(values, dtype=float)


def set_matplotlib_visibility(axis, visible):
    if visible:
        axis.set_axis_on()
    else:
        axis.set_axis_off()


def current_recording_limits(engine):
    x_axis = engine.current_axis_layout("x")
    y_axis = engine.current_axis_layout("y")
    x_limits = x_axis.get("range", [np.nan, np.nan])
    y_limits = y_axis.get("range", [np.nan, np.nan])

    return np.asarray([*x_limits, *y_limits], dtype=float)


def set_recording_limits(engine, limits):
    x_axis = engine.current_axis_layout("x")
    y_axis = engine.current_axis_layout("y")

    x_axis["range"] = recording_pair(limits[0:2])
    y_axis["range"] = recording_pair(limits[2:4])
    x_axis["autorange"] = False
    y_axis["autorange"] = False


def recording_pair(values):
    return [
        None if math.isinf(value) else float(value)
        for value in values
    ]


def apply_recording_axis_command(engine, command):
    x_axis = engine.current_axis_layout("x")
    y_axis = engine.current_axis_layout("y")

    if command == "on":
        set_recording_visibility(engine, True)
    elif command == "off":
        set_recording_visibility(engine, False)
    elif command == "manual":
        x_axis["autorange"] = False
        y_axis["autorange"] = False
    elif command == "auto":
        x_axis["autorange"] = True
        y_axis["autorange"] = True
        x_axis.pop("range", None)
        y_axis.pop("range", None)
    elif command.startswith("auto "):
        axes = command.removeprefix("auto ")

        if "x" in axes:
            x_axis["autorange"] = True
            x_axis.pop("range", None)

        if "y" in axes:
            y_axis["autorange"] = True
            y_axis.pop("range", None)
    elif command in {"tight", "padded", "tickaligned"}:
        x_axis["rangemode"] = command
        y_axis["rangemode"] = command
        x_axis["autorange"] = True
        y_axis["autorange"] = True
    elif command in {"equal", "image"}:
        y_axis["scaleanchor"] = engine.axis_reference("x")

        if command == "image":
            x_axis["rangemode"] = "tight"
            y_axis["rangemode"] = "tight"
    elif command == "square":
        x_axis["constrain"] = "domain"
        y_axis["constrain"] = "domain"
    elif command in {"fill", "normal"}:
        y_axis.pop("scaleanchor", None)
        x_axis.pop("constrain", None)
        y_axis.pop("constrain", None)
    elif command == "ij":
        y_axis["autorange"] = "reversed"
    elif command == "xy":
        if y_axis.get("autorange") == "reversed":
            y_axis["autorange"] = True
    elif command == "vis3d":
        x_axis["fixedrange"] = True
        y_axis["fixedrange"] = True
    else:
        raise MathToolRuntimeError(
            f"axis: unknown option '{command}'"
        )


def set_recording_visibility(engine, visible):
    engine.current_axis_layout("x")["visible"] = visible
    engine.current_axis_layout("y")["visible"] = visible


def is_visibility_argument(value):
    if isinstance(value, str):
        return value.lower() in {"on", "off"}

    if isinstance(value, (bool, np.bool_)):
        return True

    if isinstance(value, (int, float, np.integer, np.floating)):
        return value in {0, 1}

    return False


def visibility_value(value):
    if isinstance(value, str):
        return value.lower() == "on"

    return bool(value)
