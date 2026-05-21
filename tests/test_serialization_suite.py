import json
import math

import numpy as np

from core.engine import MathToolSession
from core.plotting.recording import RecordingPlotEngine
from core.serialization import (
    serialize_execution_result,
    serialize_plots,
    serialize_value,
    serialize_workspace,
)
from core.runtime.context import RuntimeContext
from core.runtime.symbolic import (
    SymbolicEquation,
    SymbolicValue,
)


def assert_json_safe(value):
    json.dumps(value, allow_nan=False)


def test_serialize_numpy_array_includes_shape_dtype_and_data():
    value = np.array(
        [
            [1, 2],
            [3, 4],
        ],
        dtype=float,
    )

    serialized = serialize_value(value)

    assert serialized == {
        "type": "array",
        "shape": [2, 2],
        "dtype": "float64",
        "is_complex": False,
        "data": [
            [1.0, 2.0],
            [3.0, 4.0],
        ],
    }
    assert_json_safe(serialized)


def test_serialize_complex_scalar_and_array_are_json_safe():
    scalar = serialize_value(1 + 2j)
    array = serialize_value(
        np.array([1 + 2j, 3 - 4j])
    )

    assert scalar == {
        "type": "complex",
        "real": 1.0,
        "imag": 2.0,
    }
    assert array["type"] == "array"
    assert array["is_complex"] is True
    assert array["data"] == [
        {
            "real": 1.0,
            "imag": 2.0,
        },
        {
            "real": 3.0,
            "imag": -4.0,
        },
    ]
    assert_json_safe(scalar)
    assert_json_safe(array)


def test_serialize_non_finite_numbers_without_json_nan_literals():
    serialized = serialize_value(
        np.array([math.nan, math.inf, -math.inf])
    )

    assert serialized["data"] == [
        {
            "special": "nan",
        },
        {
            "special": "inf",
        },
        {
            "special": "-inf",
        },
    ]
    assert_json_safe(serialized)


def test_serialize_symbolic_values_and_structs():
    serialized = serialize_value(
        {
            "x": SymbolicValue("x"),
            "eq": SymbolicEquation("x", "1"),
        }
    )

    assert serialized == {
        "type": "struct",
        "fields": {
            "x": {
                "type": "symbolic",
                "kind": "value",
                "expression": "x",
            },
            "eq": {
                "type": "symbolic",
                "kind": "equation",
                "expression": "x == 1",
                "left": "x",
                "right": "1",
            },
        },
    }
    assert_json_safe(serialized)


def test_serialize_workspace_hides_reserved_constants_by_default():
    context = RuntimeContext()
    context.set_variable("A", np.array([1, 2]))
    context.set_variable("z", 1 + 2j)

    serialized = serialize_workspace(context)

    assert [
        variable["name"]
        for variable in serialized["variables"]
    ] == ["A", "z"]
    assert serialized["variables"][0]["value_type"] == "array"
    assert serialized["variables"][1]["value_type"] == "complex"
    assert_json_safe(serialized)


def test_serialize_execution_result_can_include_workspace():
    session = MathToolSession()

    result = session.execute("A = [1 2; 3 4];")

    serialized = serialize_execution_result(
        result,
        context=session.context,
        include_workspace=True,
    )

    assert serialized["type"] == "execution_result"
    assert serialized["value"]["type"] == "array"
    assert serialized["workspace"]["variables"][0]["name"] == "A"
    assert_json_safe(serialized)


def test_serialize_execution_result_can_include_plots():
    session = MathToolSession(
        plot_engine=RecordingPlotEngine()
    )

    result = session.execute(
        """
x = [1 2 3];
y = [4 5 6];
plot(x, y);
title("Line");
"""
    )

    serialized = serialize_execution_result(
        result,
        context=session.context,
        include_plots=True,
    )

    assert serialized["plots"][0]["data"][0]["x"] == [
        1,
        2,
        3,
    ]
    assert (
        serialized["plots"][0]["layout"]["title"]["text"]
        == "Line"
    )
    assert_json_safe(serialized)


def test_serialize_plots_returns_empty_list_for_non_recording_engine():
    class PlotEngineWithoutSerialization:
        pass

    assert serialize_plots(
        PlotEngineWithoutSerialization()
    ) == []
