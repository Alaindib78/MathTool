import math
from numbers import Integral, Real

import numpy as np

from core.runtime.context import RESERVED_CONSTANTS
from core.runtime.formatting import format_value
from core.runtime.symbolic import (
    NameValueOption,
    SymbolicEquation,
    SymbolicValue,
)


def serialize_value(value):
    if value is None:
        return {
            "type": "none",
            "value": None,
        }

    if isinstance(value, bool):
        return {
            "type": "bool",
            "value": value,
        }

    if isinstance(value, np.ndarray):
        return serialize_array(value)

    if isinstance(value, np.generic):
        return serialize_numpy_scalar(value)

    if isinstance(value, complex):
        return serialize_complex(value)

    if isinstance(value, Integral):
        return {
            "type": "number",
            "kind": "integer",
            "value": int(value),
        }

    if isinstance(value, Real):
        return {
            "type": "number",
            "kind": "float",
            "value": json_number(float(value)),
        }

    if isinstance(value, str):
        return {
            "type": "string",
            "value": value,
        }

    if isinstance(value, SymbolicEquation):
        return {
            "type": "symbolic",
            "kind": "equation",
            "expression": value.expression,
            "left": value.left,
            "right": value.right,
        }

    if isinstance(value, SymbolicValue):
        return {
            "type": "symbolic",
            "kind": "value",
            "expression": str(value),
        }

    if isinstance(value, NameValueOption):
        return {
            "type": "option",
            "name": value.name,
            "value": serialize_value(value.value),
        }

    if isinstance(value, dict):
        return {
            "type": "struct",
            "fields": {
                str(key): serialize_value(field_value)
                for key, field_value in value.items()
            },
        }

    if isinstance(value, tuple):
        return {
            "type": "tuple",
            "items": [
                serialize_value(item)
                for item in value
            ],
        }

    if isinstance(value, list):
        return {
            "type": "list",
            "items": [
                serialize_value(item)
                for item in value
            ],
        }

    return {
        "type": "object",
        "class": type(value).__name__,
        "repr": repr(value),
    }


def serialize_numpy_scalar(value):
    scalar = value.item()
    serialized = serialize_value(scalar)
    serialized["dtype"] = str(value.dtype)
    return serialized


def serialize_array(value):
    array = np.asarray(value)

    return {
        "type": "array",
        "shape": list(array.shape),
        "dtype": str(array.dtype),
        "is_complex": bool(np.iscomplexobj(array)),
        "data": serialize_array_data(array),
    }


def serialize_array_data(array):
    if array.ndim == 0:
        return json_leaf(array.item())

    return json_leaf(array.tolist())


def serialize_complex(value):
    return {
        "type": "complex",
        "real": json_number(float(value.real)),
        "imag": json_number(float(value.imag)),
    }


def serialize_workspace(
    context_or_variables,
    *,
    include_reserved=False,
):
    variables = getattr(
        context_or_variables,
        "variables",
        context_or_variables,
    )

    return {
        "type": "workspace",
        "variables": [
            serialize_variable(name, value)
            for name, value in sorted(
                variables.items(),
                key=lambda item: item[0],
            )
            if (
                include_reserved
                or name not in RESERVED_CONSTANTS
            )
        ],
    }


def serialize_variable(name, value):
    serialized_value = serialize_value(value)

    return {
        "name": name,
        "value_type": serialized_value["type"],
        "preview": format_value(value),
        "value": serialized_value,
    }


def serialize_execution_result(
    result,
    *,
    context=None,
    include_workspace=False,
):
    payload = {
        "type": "execution_result",
        "value": serialize_value(result.value),
        "output": list(result.output),
        "source_path": result.source_path,
        "command": result.command,
        "workspace_changed": result.workspace_changed,
        "clear_output": result.clear_output,
        "should_exit": result.should_exit,
    }

    if include_workspace:
        if context is None:
            raise ValueError(
                "context is required when include_workspace=True"
            )

        payload["workspace"] = serialize_workspace(
            context
        )

    return payload


def json_leaf(value):
    if isinstance(value, list):
        return [
            json_leaf(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            json_leaf(item)
            for item in value
        ]

    if isinstance(value, np.generic):
        return json_leaf(value.item())

    if isinstance(value, complex):
        return {
            "real": json_number(float(value.real)),
            "imag": json_number(float(value.imag)),
        }

    if isinstance(value, bool):
        return value

    if isinstance(value, Integral):
        return int(value)

    if isinstance(value, Real):
        return json_number(float(value))

    if value is None or isinstance(value, str):
        return value

    return serialize_value(value)


def json_number(value):
    if math.isfinite(value):
        return value

    if math.isnan(value):
        special = "nan"
    elif value > 0:
        special = "inf"
    else:
        special = "-inf"

    return {
        "special": special,
    }
