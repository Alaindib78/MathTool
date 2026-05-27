from __future__ import annotations

import math
import struct
from dataclasses import dataclass
from fractions import Fraction
from numbers import Integral, Real
from threading import RLock

import numpy as np


NUMERIC_FORMATS = {
    "short",
    "long",
    "shortE",
    "longE",
    "shortG",
    "longG",
    "shortEng",
    "longEng",
    "bank",
    "rat",
    "hex",
    "+",
}

SPACING_MODES = {
    "compact",
    "loose",
}

FORMAT_ALIASES = {
    "default": "default",
    "short": "short",
    "long": "long",
    "shorte": "shortE",
    "longe": "longE",
    "shortg": "shortG",
    "longg": "longG",
    "shorteng": "shortEng",
    "longeng": "longEng",
    "bank": "bank",
    "rat": "rat",
    "rational": "rat",
    "hex": "hex",
    "+": "+",
    "compact": "compact",
    "loose": "loose",
    "short e": "shortE",
    "long e": "longE",
    "short g": "shortG",
    "long g": "longG",
    "short eng": "shortEng",
    "long eng": "longEng",
}


@dataclass(frozen=True)
class DisplaySettings:
    numeric_format: str = "short"
    spacing_mode: str = "loose"

    @property
    def precision(self):
        return {
            "short": 4,
            "long": 15,
            "shortE": 4,
            "longE": 15,
            "shortG": 5,
            "longG": 15,
            "shortEng": 4,
            "longEng": 15,
            "bank": 2,
        }.get(self.numeric_format)

    @property
    def scientific_mode(self):
        return self.numeric_format in {
            "shortE",
            "longE",
            "shortG",
            "longG",
        }

    @property
    def engineering_mode(self):
        return self.numeric_format in {
            "shortEng",
            "longEng",
        }


class DisplayFormatManager:
    def __init__(self, settings=None):
        self._settings = settings or DisplaySettings()
        self._lock = RLock()

    @property
    def settings(self):
        with self._lock:
            return self._settings

    def reset(self):
        with self._lock:
            self._settings = DisplaySettings()

        return self.settings

    def apply(self, *styles):
        flattened = normalize_style_arguments(styles)

        if not flattened:
            return self.reset()

        with self._lock:
            settings = self._settings

            for style in flattened:
                canonical = canonical_format_style(style)

                if canonical == "default":
                    settings = DisplaySettings()
                elif canonical in NUMERIC_FORMATS:
                    settings = DisplaySettings(
                        numeric_format=canonical,
                        spacing_mode=settings.spacing_mode,
                    )
                elif canonical in SPACING_MODES:
                    settings = DisplaySettings(
                        numeric_format=settings.numeric_format,
                        spacing_mode=canonical,
                    )
                else:
                    raise ValueError(
                        f"Unsupported format style '{style}'"
                    )

            self._settings = settings

        return self.settings

    def format(self, value):
        return OutputFormatter(self.settings).format(value)

    def format_number(self, value):
        return OutputFormatter(self.settings).format_number(value)

    def output_suffix(self):
        return "\n" if self.settings.spacing_mode == "compact" else "\n\n"


class OutputFormatter:
    def __init__(self, settings=None):
        self.settings = settings or DisplaySettings()

    def format(self, value):
        if isinstance(value, dict):
            return self.format_struct(value)

        if isinstance(value, np.ndarray):
            return self.format_array(value)

        if isinstance(value, np.generic):
            value = value.item()

        if isinstance(value, str):
            return value

        if isinstance(value, (bool, np.bool_)):
            return "true" if value else "false"

        if isinstance(value, complex):
            return self.format_complex(value)

        if is_numeric_scalar(value):
            return self.format_number(value)

        return str(value)

    def format_struct(self, value):
        if not value:
            return "struct with no fields"

        fields = "\n".join(
            f"    {key}: {self.format_struct_field_value(field_value)}"
            for key, field_value in value.items()
        )

        return f"struct with fields:\n{fields}"

    def format_struct_field_value(self, value):
        if isinstance(value, str):
            return f"'{value}'"

        return self.format(value)

    def format_array(self, value):
        array = np.asarray(value)

        if array.ndim == 0:
            return self.format(array.item())

        if array.size == 0:
            return "[]"

        if np.iscomplexobj(array):
            return self.format_complex_array(array)

        return np.array2string(
            array,
            separator=" ",
            formatter={"all": self.format_array_cell},
        )

    def format_array_cell(self, value):
        if isinstance(value, np.generic):
            value = value.item()

        if isinstance(value, (bool, np.bool_)):
            return "true" if value else "false"

        if isinstance(value, complex):
            return self.format_complex(value)

        if is_numeric_scalar(value):
            return self.format_number(value)

        return str(value)

    def format_complex_array(self, value):
        array = np.asarray(value)

        rows = array

        if rows.ndim == 1:
            rows = rows.reshape(1, -1)

        shape = "x".join(
            str(size)
            for size in array.shape
        )

        body = "\n".join(
            "   "
            + "   ".join(
                self.format_complex(cell)
                for cell in row
            )
            for row in rows
        )

        return f"{shape} complex\n\n{body}"

    def format_complex(self, value):
        real = normalize_zero(float(value.real))
        imag = normalize_zero(float(value.imag))
        sign = "+" if imag >= 0 else "-"

        return (
            f"{self.format_number(real)} {sign} "
            f"{self.format_number(abs(imag))}i"
        )

    def format_number(self, value):
        if isinstance(value, np.generic):
            value = value.item()

        if isinstance(value, (bool, np.bool_)):
            return "true" if value else "false"

        if isinstance(value, Integral):
            if self.settings.numeric_format == "hex":
                return format_hex_number(value)

            if self.settings.numeric_format == "rat":
                return str(int(value))

            if self.settings.numeric_format == "+":
                return format_sign_number(value)

            return str(int(value))

        value = normalize_zero(float(value))
        numeric_format = self.settings.numeric_format

        if numeric_format == "short":
            return format_fixed(value, 4)

        if numeric_format == "long":
            return format_fixed(value, 15)

        if numeric_format == "shortE":
            return format_scientific(value, 4)

        if numeric_format == "longE":
            return format_scientific(value, 15)

        if numeric_format == "shortG":
            return format_general(value, 5)

        if numeric_format == "longG":
            return format_general(value, 15)

        if numeric_format == "shortEng":
            return format_engineering(value, 4, significant=False)

        if numeric_format == "longEng":
            return format_engineering(value, 15, significant=True)

        if numeric_format == "bank":
            return format_fixed(value, 2)

        if numeric_format == "rat":
            return format_rational(value)

        if numeric_format == "hex":
            return format_hex_number(value)

        if numeric_format == "+":
            return format_sign_number(value)

        return format_general(value, 12)


def normalize_style_arguments(styles):
    result = []

    for style in styles:
        if style is None:
            continue

        if isinstance(style, np.generic):
            style = style.item()

        text = str(style).strip()

        if not text:
            continue

        if " " in text:
            collapsed = " ".join(text.split())

            if collapsed.lower() in FORMAT_ALIASES:
                result.append(collapsed)
            else:
                result.extend(collapsed.split())
        else:
            result.append(text)

    return combine_separate_precision_styles(result)


def combine_separate_precision_styles(styles):
    result = []
    index = 0

    while index < len(styles):
        current = styles[index]
        next_value = styles[index + 1] if index + 1 < len(styles) else None
        combined = (
            f"{current} {next_value}"
            if next_value is not None
            else None
        )

        if combined is not None and combined.lower() in FORMAT_ALIASES:
            result.append(combined)
            index += 2
        else:
            result.append(current)
            index += 1

    return result


def canonical_format_style(style):
    key = str(style).strip()

    if key == "+":
        return "+"

    normalized = " ".join(key.split()).lower()

    if normalized in FORMAT_ALIASES:
        return FORMAT_ALIASES[normalized]

    raise ValueError(f"Unsupported format style '{style}'")


def format_value(value, display_format=None):
    manager = display_format or DEFAULT_DISPLAY_FORMAT_MANAGER
    settings = (
        manager.settings
        if isinstance(manager, DisplayFormatManager)
        else manager
    )

    return OutputFormatter(settings).format(value)


def format_number(value, display_format=None):
    manager = display_format or DEFAULT_DISPLAY_FORMAT_MANAGER
    settings = (
        manager.settings
        if isinstance(manager, DisplayFormatManager)
        else manager
    )

    return OutputFormatter(settings).format_number(value)


def output_suffix(display_format=None):
    manager = display_format or DEFAULT_DISPLAY_FORMAT_MANAGER

    if isinstance(manager, DisplayFormatManager):
        return manager.output_suffix()

    return "\n" if manager.spacing_mode == "compact" else "\n\n"


def is_numeric_scalar(value):
    return isinstance(value, (Integral, Real, np.number)) and not isinstance(
        value,
        (bool, np.bool_),
    )


def normalize_zero(value):
    if abs(value) < 1e-12:
        return 0.0

    return value


def format_fixed(value, decimals):
    if not math.isfinite(value):
        return format_special_float(value)

    return f"{value:.{decimals}f}"


def format_scientific(value, decimals):
    if not math.isfinite(value):
        return format_special_float(value)

    return f"{value:.{decimals}e}"


def format_general(value, significant_digits):
    if not math.isfinite(value):
        return format_special_float(value)

    return f"{value:.{significant_digits}g}"


def format_engineering(value, precision, *, significant):
    if not math.isfinite(value):
        return format_special_float(value)

    if value == 0:
        exponent = 0
        mantissa = 0.0
    else:
        exponent = int(math.floor(math.log10(abs(value)) / 3) * 3)
        mantissa = value / (10 ** exponent)

    if significant:
        integer_digits = len(str(int(abs(mantissa)))) if mantissa else 1
        decimals = max(0, precision - integer_digits)
    else:
        decimals = precision

    return f"{mantissa:.{decimals}f}e{exponent:+04d}"


def format_rational(value):
    if not math.isfinite(value):
        return format_special_float(value)

    value = normalize_zero(value)

    if value == 0:
        return "0"

    fraction = Fraction(value).limit_denominator(1000)

    if fraction.denominator == 1:
        return str(fraction.numerator)

    return f"{fraction.numerator}/{fraction.denominator}"


def format_hex_number(value):
    if isinstance(value, np.generic):
        value = value.item()

    try:
        packed = struct.pack(">d", float(value))
    except (OverflowError, TypeError, ValueError):
        packed = struct.pack(">q", int(value))

    return packed.hex()


def format_sign_number(value):
    value = float(value)

    if value > 0:
        return "+"

    if value < 0:
        return "-"

    return " "


def format_special_float(value):
    if math.isnan(value):
        return "NaN"

    if value > 0:
        return "Inf"

    return "-Inf"


DEFAULT_DISPLAY_FORMAT_MANAGER = DisplayFormatManager()
