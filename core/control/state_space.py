from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from core.control.lti import (
    LTIModel,
    as_numeric_array,
    format_matrix,
)
from core.errors.errors import RuntimeError as MathToolRuntimeError


def matrix_for_role(value, name, rows=None, cols=None):
    array = as_numeric_array(value, name, "ss")

    if array.ndim == 0:
        array = array.reshape(1, 1)
    elif array.ndim == 1:
        if name == "B":
            array = array.reshape(-1, 1)
        else:
            array = array.reshape(1, -1)
    elif array.ndim != 2:
        raise MathToolRuntimeError(
            f"ss: {name} must be a two-dimensional matrix"
        )

    if rows is not None and array.shape[0] != rows:
        raise MathToolRuntimeError(
            f"ss: {name} matrix must have {rows} row(s)"
        )

    if cols is not None and array.shape[1] != cols:
        raise MathToolRuntimeError(
            f"ss: {name} matrix must have {cols} column(s)"
        )

    return np.real_if_close(array, tol=1000)


@dataclass
class StateSpaceModel(LTIModel):
    A: object = None
    B: object = None
    C: object = None
    D: object = None

    def __init__(self, A, B, C, D, Ts=0.0, **metadata):
        super().__init__(
            "ss",
            Ts=Ts,
            input_delay=metadata.pop("input_delay", 0.0),
            output_delay=metadata.pop("output_delay", 0.0),
            io_delay=metadata.pop("io_delay", 0.0),
            name=metadata.pop("name", ""),
            input_name=metadata.pop("input_name", []),
            output_name=metadata.pop("output_name", []),
            input_unit=metadata.pop("input_unit", []),
            output_unit=metadata.pop("output_unit", []),
            notes=metadata.pop("notes", []),
            user_data=metadata.pop("user_data", None),
        )
        self.A = matrix_for_role(A, "A")
        self.B = matrix_for_role(B, "B")
        self.C = matrix_for_role(C, "C")
        self.D = matrix_for_role(D, "D")
        self.validate()

    def validate(self):
        if self.A.shape[0] != self.A.shape[1]:
            raise MathToolRuntimeError("ss: A matrix must be square")

        states = self.A.shape[0]

        if self.B.shape[0] != states:
            raise MathToolRuntimeError(
                "ss: B matrix row count must match A"
            )

        if self.C.shape[1] != states:
            raise MathToolRuntimeError(
                "ss: C matrix column count must match A"
            )

        outputs = self.C.shape[0]
        inputs = self.B.shape[1]

        if self.D.shape != (outputs, inputs):
            raise MathToolRuntimeError(
                "ss: D dimensions must match C outputs and B inputs"
            )

    def properties(self):
        properties = {
            "A": self.A,
            "B": self.B,
            "C": self.C,
            "D": self.D,
        }
        properties.update(self.common_properties())
        return properties

    def set_property(self, name, value):
        key = str(name).lower()

        if key in {"a", "b", "c", "d"}:
            setattr(self, key.upper(), matrix_for_role(value, key.upper()))
            self.validate()
            return self

        return super().set_property(name, value)

    def __str__(self):
        lines = [
            "State-space model:",
            "",
            "A =",
            format_matrix(self.A),
            "",
            "B =",
            format_matrix(self.B),
            "",
            "C =",
            format_matrix(self.C),
            "",
            "D =",
            format_matrix(self.D),
            "",
            self.time_description(),
        ]
        delays = self.delay_description()
        if delays:
            lines.append(delays)
        return "\n".join(lines)

    def workspace_preview(self):
        timing = (
            f"discrete-time, Ts={self.Ts:g}"
            if self.is_discrete
            else "continuous-time"
        )
        states = self.A.shape[0]
        inputs = self.B.shape[1]
        outputs = self.C.shape[0]

        return (
            f"ss model, {states} states, "
            f"{inputs} input, {outputs} output, {timing}"
        )
