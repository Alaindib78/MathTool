from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from core.control.lti import (
    LTIModel,
    as_numeric_array,
    format_matrix,
)
from core.errors.errors import RuntimeError as MathToolRuntimeError


@dataclass
class FrequencyResponseModel(LTIModel):
    response: object = None
    frequencies: object = None

    def __init__(self, response, frequencies, Ts=0.0, **metadata):
        super().__init__(
            "frd",
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
        self.response = as_numeric_array(response, "response", "frd")
        self.frequencies = as_numeric_array(
            frequencies,
            "frequencies",
            "frd",
        ).reshape(-1)
        self.validate()

    def validate(self):
        if self.frequencies.size == 0:
            raise MathToolRuntimeError("frd: frequencies cannot be empty")

        if np.any(np.real(self.frequencies) <= 0):
            raise MathToolRuntimeError(
                "frd: frequencies must be positive"
            )

        if self.response.reshape(-1).size != self.frequencies.size:
            raise MathToolRuntimeError(
                "frd: response and frequencies must have matching lengths"
            )

    def properties(self):
        properties = {
            "Response": self.response,
            "Frequencies": self.frequencies,
            "response": self.response,
            "frequencies": self.frequencies,
        }
        properties.update(self.common_properties())
        return properties

    def __str__(self):
        return "\n".join(
            [
                "Frequency-response data model:",
                "",
                "Frequencies =",
                format_matrix(self.frequencies),
                "",
                "Response =",
                format_matrix(self.response),
                "",
                self.time_description(),
            ]
        )
