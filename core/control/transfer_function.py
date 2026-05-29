from __future__ import annotations

from dataclasses import dataclass
from numbers import Number

import numpy as np

from core.control.lti import (
    LTIModel,
    as_vector,
    format_polynomial,
    fraction_text,
    real_if_close,
    trim_leading_zeros,
)
from core.errors.errors import RuntimeError as MathToolRuntimeError


@dataclass
class TransferFunctionModel(LTIModel):
    numerator: object = None
    denominator: object = None

    def __init__(
        self,
        numerator,
        denominator,
        Ts=0.0,
        **metadata,
    ):
        super().__init__(
            "tf",
            Ts=Ts,
            input_delay=metadata.pop("input_delay", 0.0),
            output_delay=metadata.pop("output_delay", 0.0),
            io_delay=metadata.pop("io_delay", 0.0),
            name=metadata.pop("name", ""),
            input_name=metadata.pop("input_name", []),
            output_name=metadata.pop("output_name", []),
            notes=metadata.pop("notes", []),
            user_data=metadata.pop("user_data", None),
        )
        self.numerator = as_vector(numerator, "numerator", "tf")
        self.denominator = as_vector(denominator, "denominator", "tf")
        self.validate()

    @classmethod
    def variable(cls, variable="s", Ts=0.0):
        if variable not in {"s", "z"}:
            raise MathToolRuntimeError(
                "tf: transfer variable must be 's' or 'z'"
            )

        if variable == "z" and (Ts is None or float(Ts) <= 0):
            raise MathToolRuntimeError(
                "tf: transfer variable 'z' requires a positive sample time"
            )

        return cls([1, 0], [1], 0.0 if variable == "s" else Ts)

    def validate(self):
        if self.denominator.size == 0:
            raise MathToolRuntimeError("tf: denominator cannot be empty")

        if np.isclose(self.denominator[0], 0):
            raise MathToolRuntimeError(
                "tf: leading denominator coefficient cannot be zero"
            )

        self.numerator = real_if_close(self.numerator.reshape(-1))
        self.denominator = real_if_close(self.denominator.reshape(-1))

    def properties(self):
        properties = {
            "Numerator": self.numerator,
            "Denominator": self.denominator,
            "numerator": self.numerator,
            "denominator": self.denominator,
        }
        properties.update(self.common_properties())
        return properties

    def set_property(self, name, value):
        key = str(name).lower()

        if key in {"numerator", "num"}:
            self.numerator = as_vector(value, "numerator", "tf")
            self.validate()
            return self

        if key in {"denominator", "den"}:
            self.denominator = as_vector(value, "denominator", "tf")
            self.validate()
            return self

        return super().set_property(name, value)

    def __str__(self):
        numerator = format_polynomial(
            self.numerator,
            self.time_variable,
        )
        denominator = format_polynomial(
            self.denominator,
            self.time_variable,
        )
        lines = [
            "Transfer function:",
            fraction_text(numerator, denominator),
            self.time_description(),
        ]
        delays = self.delay_description()
        if delays:
            lines.append(delays)
        return "\n".join(lines)

    def _coerce(self, other):
        if isinstance(other, TransferFunctionModel):
            self._ensure_compatible_sample_time(other)
            return other

        if isinstance(other, Number) or isinstance(other, np.number):
            return TransferFunctionModel([other], [1], self.Ts)

        return NotImplemented

    def _ensure_compatible_sample_time(self, other):
        if not np.isclose(self.Ts, other.Ts):
            raise MathToolRuntimeError(
                "tf: sample times must match for transfer-function arithmetic"
            )

    def __neg__(self):
        return TransferFunctionModel(-self.numerator, self.denominator, self.Ts)

    def __add__(self, other):
        other = self._coerce(other)
        if other is NotImplemented:
            return NotImplemented

        numerator = np.polyadd(
            np.convolve(self.numerator, other.denominator),
            np.convolve(other.numerator, self.denominator),
        )
        denominator = np.convolve(self.denominator, other.denominator)
        return TransferFunctionModel(
            trim_leading_zeros(numerator),
            trim_leading_zeros(denominator),
            self.Ts,
        )

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        other = self._coerce(other)
        if other is NotImplemented:
            return NotImplemented

        return self.__add__(-other)

    def __rsub__(self, other):
        return (-self).__add__(other)

    def __mul__(self, other):
        other = self._coerce(other)
        if other is NotImplemented:
            return NotImplemented

        return TransferFunctionModel(
            trim_leading_zeros(np.convolve(self.numerator, other.numerator)),
            trim_leading_zeros(np.convolve(self.denominator, other.denominator)),
            self.Ts,
        )

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        other = self._coerce(other)
        if other is NotImplemented:
            return NotImplemented

        if np.all(np.isclose(other.numerator, 0)):
            raise MathToolRuntimeError("tf: division by zero transfer function")

        return TransferFunctionModel(
            trim_leading_zeros(np.convolve(self.numerator, other.denominator)),
            trim_leading_zeros(np.convolve(self.denominator, other.numerator)),
            self.Ts,
        )

    def __rtruediv__(self, other):
        other = self._coerce(other)
        if other is NotImplemented:
            return NotImplemented

        return other.__truediv__(self)

    def __pow__(self, power):
        if isinstance(power, np.generic):
            power = power.item()

        if isinstance(power, float) and power.is_integer():
            power = int(power)

        if not isinstance(power, int) or power < 0:
            raise MathToolRuntimeError(
                "tf: power must be a nonnegative integer"
            )

        result = TransferFunctionModel([1], [1], self.Ts)

        for _ in range(power):
            result = result * self

        return result
