from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from core.control.lti import (
    LTIModel,
    as_vector,
    format_factor,
    format_scalar,
    fraction_text,
    numeric_scalar,
)


@dataclass
class ZeroPoleGainModel(LTIModel):
    zeros: object = None
    poles: object = None
    gain: object = 1.0

    def __init__(self, zeros, poles, gain, Ts=0.0, **metadata):
        super().__init__(
            "zpk",
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
        self.zeros = as_vector(zeros, "zeros", "zpk", allow_empty=True)
        self.poles = as_vector(poles, "poles", "zpk", allow_empty=True)
        self.gain = numeric_scalar(gain, "gain", "zpk")

    def properties(self):
        properties = {
            "Zeros": self.zeros,
            "Poles": self.poles,
            "Gain": self.gain,
            "zeros": self.zeros,
            "poles": self.poles,
            "gain": self.gain,
        }
        properties.update(self.common_properties())
        return properties

    def set_property(self, name, value):
        key = str(name).lower()

        if key in {"zeros", "zero", "z"}:
            self.zeros = as_vector(value, "zeros", "zpk", allow_empty=True)
            return self

        if key in {"poles", "pole", "p"}:
            self.poles = as_vector(value, "poles", "zpk", allow_empty=True)
            return self

        if key in {"gain", "k"}:
            self.gain = numeric_scalar(value, "gain", "zpk")
            return self

        return super().set_property(name, value)

    def __str__(self):
        variable = self.time_variable
        zero_terms = " ".join(format_factor(root, variable) for root in self.zeros)
        pole_terms = " ".join(format_factor(root, variable) for root in self.poles)
        numerator = format_scalar(self.gain)

        if zero_terms:
            numerator = f"{numerator} {zero_terms}"

        denominator = pole_terms or "1"

        lines = [
            "Zero/pole/gain:",
            fraction_text(numerator, denominator),
            self.time_description(),
        ]
        delays = self.delay_description()
        if delays:
            lines.append(delays)
        return "\n".join(lines)
