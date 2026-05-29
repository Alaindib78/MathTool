from __future__ import annotations

from dataclasses import dataclass, field
from numbers import Number

import numpy as np

from core.errors.errors import RuntimeError as MathToolRuntimeError


def is_lti_model(value):
    return isinstance(value, LTIModel)


def validate_sample_time(value, function_name="lti"):
    if value is None:
        return 0.0

    if isinstance(value, np.ndarray):
        if value.size != 1:
            raise MathToolRuntimeError(
                f"{function_name}: sample time Ts must be a scalar"
            )
        value = value.reshape(-1)[0]

    if isinstance(value, np.generic):
        value = value.item()

    if isinstance(value, bool) or not isinstance(value, Number):
        raise MathToolRuntimeError(
            f"{function_name}: sample time Ts must be numeric"
        )

    sample_time = float(np.real(value))

    if not np.isfinite(sample_time) or sample_time < 0:
        raise MathToolRuntimeError(
            f"{function_name}: sample time Ts must be finite and nonnegative"
        )

    return sample_time


def validate_delay(value, name, function_name="lti"):
    if value is None:
        return 0.0

    if isinstance(value, np.ndarray):
        if value.size != 1:
            raise MathToolRuntimeError(
                f"{function_name}: {name} must be a scalar"
            )
        value = value.reshape(-1)[0]

    if isinstance(value, np.generic):
        value = value.item()

    if isinstance(value, bool) or not isinstance(value, Number):
        raise MathToolRuntimeError(
            f"{function_name}: {name} must be numeric"
        )

    delay = float(np.real(value))

    if not np.isfinite(delay) or delay < 0:
        raise MathToolRuntimeError(
            f"{function_name}: {name} must be finite and nonnegative"
        )

    return delay


def as_numeric_array(value, name, function_name, *, allow_empty=False):
    try:
        array = np.asarray(value, dtype=complex)
    except (TypeError, ValueError) as error:
        raise MathToolRuntimeError(
            f"{function_name}: {name} must be numeric"
        ) from error

    if array.size == 0 and not allow_empty:
        raise MathToolRuntimeError(
            f"{function_name}: {name} cannot be empty"
        )

    if array.size and not np.all(np.isfinite(array)):
        raise MathToolRuntimeError(
            f"{function_name}: {name} values must be finite"
        )

    return real_if_close(array)


def as_vector(value, name, function_name, *, allow_empty=False):
    return as_numeric_array(
        value,
        name,
        function_name,
        allow_empty=allow_empty,
    ).reshape(-1)


def real_if_close(value):
    return np.real_if_close(value, tol=1000)


def numeric_scalar(value, name, function_name):
    array = as_numeric_array(value, name, function_name)

    if array.size != 1:
        raise MathToolRuntimeError(
            f"{function_name}: {name} must be a scalar"
        )

    scalar = array.reshape(-1)[0]

    if isinstance(scalar, np.generic):
        scalar = scalar.item()

    return scalar


def trim_leading_zeros(coefficients):
    coeffs = np.asarray(coefficients, dtype=complex).reshape(-1)

    if coeffs.size == 0:
        return coeffs

    index = 0
    while index < coeffs.size - 1 and np.isclose(coeffs[index], 0):
        index += 1

    return real_if_close(coeffs[index:])


def format_scalar(value):
    if isinstance(value, np.generic):
        value = value.item()

    if isinstance(value, complex) or np.iscomplexobj(value):
        value = complex(value)
        real = 0.0 if abs(value.real) < 1e-12 else value.real
        imag = 0.0 if abs(value.imag) < 1e-12 else value.imag

        if imag == 0:
            return f"{real:.6g}"

        if real == 0:
            return f"{imag:.6g}i"

        sign = "+" if imag >= 0 else "-"
        return f"{real:.6g} {sign} {abs(imag):.6g}i"

    value = float(value)
    if abs(value) < 1e-12:
        value = 0.0

    return f"{value:.6g}"


def format_matrix(value):
    array = np.asarray(value)

    if array.size == 0:
        return "[]"

    return np.array2string(
        real_if_close(array),
        separator=" ",
        formatter={"all": lambda cell: format_scalar(cell)},
    )


def format_polynomial(coefficients, variable):
    coeffs = trim_leading_zeros(coefficients)

    if coeffs.size == 0 or np.all(np.isclose(coeffs, 0)):
        return "0"

    degree = coeffs.size - 1
    parts = []

    for index, coefficient in enumerate(coeffs):
        if np.isclose(coefficient, 0):
            continue

        power = degree - index
        coefficient = complex(coefficient)
        sign = "-" if coefficient.real < 0 and abs(coefficient.imag) < 1e-12 else "+"
        magnitude = -coefficient if sign == "-" else coefficient

        if power == 0:
            term = format_scalar(magnitude)
        else:
            variable_part = variable if power == 1 else f"{variable}^{power}"

            if np.isclose(magnitude, 1):
                term = variable_part
            else:
                term = f"{format_scalar(magnitude)} {variable_part}"

        if not parts:
            parts.append(f"-{term}" if sign == "-" else term)
        else:
            parts.append(f" {sign} {term}")

    return "".join(parts)


def format_factor(root, variable):
    root = complex(root)

    if abs(root.imag) < 1e-12:
        value = root.real
        if value < 0:
            return f"({variable}+{format_scalar(abs(value))})"
        if value > 0:
            return f"({variable}-{format_scalar(value)})"
        return f"{variable}"

    sign = "-" if root.real >= 0 else "+"
    real_text = format_scalar(abs(root.real))
    imag_sign = "+" if root.imag >= 0 else "-"
    imag_text = format_scalar(abs(root.imag))

    if abs(root.real) < 1e-12:
        return f"({variable} {imag_sign} {imag_text}i)"

    return f"({variable} {sign} {real_text} {imag_sign} {imag_text}i)"


def fraction_text(numerator, denominator):
    width = max(len(numerator), len(denominator), 5)
    return "\n".join(
        [
            numerator.center(width),
            "-" * width,
            denominator.center(width),
        ]
    )


@dataclass
class LTIModel:
    model_type: str
    Ts: float = 0.0
    input_delay: float = 0.0
    output_delay: float = 0.0
    io_delay: float = 0.0
    name: str = ""
    input_name: list[str] = field(default_factory=list)
    output_name: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    user_data: object = None

    def __post_init__(self):
        self.Ts = validate_sample_time(self.Ts)
        self.input_delay = validate_delay(self.input_delay, "InputDelay")
        self.output_delay = validate_delay(self.output_delay, "OutputDelay")
        self.io_delay = validate_delay(self.io_delay, "IODelay")

    @property
    def is_discrete(self):
        return self.Ts > 0

    @property
    def time_variable(self):
        return "z" if self.is_discrete else "s"

    def has_delay(self):
        return any(
            delay > 0
            for delay in (
                self.input_delay,
                self.output_delay,
                self.io_delay,
            )
        )

    def time_description(self):
        if self.is_discrete:
            return f"Sample time: {format_scalar(self.Ts)} seconds"

        return "Continuous-time model."

    def delay_description(self):
        lines = []

        if self.input_delay > 0:
            lines.append(f"InputDelay: {format_scalar(self.input_delay)}")

        if self.output_delay > 0:
            lines.append(f"OutputDelay: {format_scalar(self.output_delay)}")

        if self.io_delay > 0:
            lines.append(f"IODelay: {format_scalar(self.io_delay)}")

        return "\n".join(lines)

    def common_properties(self):
        return {
            "Ts": self.Ts,
            "InputDelay": self.input_delay,
            "OutputDelay": self.output_delay,
            "IODelay": self.io_delay,
            "InputName": list(self.input_name),
            "OutputName": list(self.output_name),
            "Name": self.name,
            "Notes": list(self.notes),
            "UserData": self.user_data,
        }

    def properties(self):
        return self.common_properties()

    def get_property(self, name):
        lookup = {key.lower(): value for key, value in self.properties().items()}
        key = str(name).lower()

        if key not in lookup:
            raise MathToolRuntimeError(
                f"{self.model_type}: unknown property '{name}'"
            )

        return lookup[key]

    def set_property(self, name, value):
        key = str(name).lower()

        if key == "ts":
            self.Ts = validate_sample_time(value)
        elif key == "inputdelay":
            self.input_delay = validate_delay(value, "InputDelay")
        elif key == "outputdelay":
            self.output_delay = validate_delay(value, "OutputDelay")
        elif key in {"iodelay", "io_delay"}:
            self.io_delay = validate_delay(value, "IODelay")
        elif key == "name":
            self.name = str(value)
        elif key == "inputname":
            self.input_name = list(np.asarray(value).reshape(-1))
        elif key == "outputname":
            self.output_name = list(np.asarray(value).reshape(-1))
        elif key == "notes":
            self.notes = list(np.asarray(value).reshape(-1))
        elif key == "userdata":
            self.user_data = value
        else:
            raise MathToolRuntimeError(
                f"{self.model_type}: property '{name}' is read-only or unknown"
            )

        return self

    def workspace_preview(self):
        return f"{self.model_type} model"

    def __repr__(self):
        return f"<{type(self).__name__} {self.workspace_preview()}>"
