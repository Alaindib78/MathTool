import math

import numpy as np

from core.engine import MathToolSession
from core.runtime.formatting import (
    DisplayFormatManager,
    format_value,
    output_suffix,
)
from core.serialization import serialize_workspace
from core.stdlib.console import disp


def test_format_command_changes_display_not_stored_value():
    session = MathToolSession()

    session.execute("x = pi;")
    session.execute(
        "format long",
        allow_commands=True,
    )

    assert session.context.variables["x"] == math.pi
    assert format_value(
        session.context.variables["x"],
        session.context.display_format,
    ) == "3.141592653589793"

    session.execute(
        "format short",
        allow_commands=True,
    )

    assert session.context.variables["x"] == math.pi
    assert format_value(
        session.context.variables["x"],
        session.context.display_format,
    ) == "3.1416"


def test_format_function_form_and_script_command_form():
    session = MathToolSession()

    session.execute('format("shortE");')

    assert format_value(
        math.pi,
        session.context.display_format,
    ) == "3.1416e+00"

    session.execute("format longG;")

    assert format_value(
        math.pi,
        session.context.display_format,
    ) == "3.14159265358979"


def test_supported_numeric_format_modes():
    manager = DisplayFormatManager()

    expected = {
        "short": "3.1416",
        "long": "3.141592653589793",
        "shortE": "3.1416e+00",
        "longE": "3.141592653589793e+00",
        "shortG": "3.1416",
        "longG": "3.14159265358979",
        "shortEng": "3.1416e+000",
        "bank": "3.14",
        "rat": "355/113",
        "hex": "400921fb54442d18",
    }

    for style, text in expected.items():
        manager.apply(style)

        assert format_value(math.pi, manager) == text

    manager.apply("longEng")

    assert format_value(5123456.789, manager) == (
        "5.12345678900000e+006"
    )


def test_sign_format_for_arrays():
    manager = DisplayFormatManager()
    manager.apply("+")

    assert format_value(np.array([-1, 0, 1]), manager) == "[-   +]"


def test_workspace_preview_uses_context_display_format():
    session = MathToolSession()
    session.execute("x = pi;")
    session.execute(
        "format long",
        allow_commands=True,
    )

    serialized = serialize_workspace(session.context)

    assert serialized["variables"][0]["preview"] == (
        "3.141592653589793"
    )


def test_disp_uses_active_format_and_spacing():
    manager = DisplayFormatManager()
    output = []

    manager.apply("short", "compact")
    disp(
        math.pi,
        output_callback=output.append,
        display_format=manager,
    )

    manager.apply("long", "loose")
    disp(
        math.pi,
        output_callback=output.append,
        display_format=manager,
    )

    assert output == [
        "3.1416\n",
        "3.141592653589793\n\n",
    ]
    assert output_suffix(manager) == "\n\n"
