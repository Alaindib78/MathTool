import sys

import numpy as np

from core.runtime.formatting import format_value


class ConsoleFormatError(ValueError):
    pass


class ConsoleAbortError(Exception):
    def __init__(self, message, *, already_reported=False):
        super().__init__(message)
        self.already_reported = already_reported


def disp(value=None, *, output_callback=None):
    text = format_console_value(value)
    write_console(text + "\n", output_callback, sys.stdout)


def fprintf(format_string, *args, output_callback=None):
    text = format_format_string(format_string, args)
    write_console(text, output_callback, sys.stdout)


def warning(message, *args, output_callback=None):
    text = "Warning: " + format_message(message, args)
    write_console(text + "\n", output_callback, sys.stderr)


def error(message, *args, output_callback=None, emit=True):
    text = "Error: " + format_message(message, args)
    already_reported = False

    if emit:
        write_console(text + "\n", output_callback, sys.stderr)
        already_reported = True

    raise ConsoleAbortError(
        text,
        already_reported=already_reported,
    )


def write_console(text, output_callback, stream):
    if output_callback is not None:
        output_callback(text)
        return

    stream.write(text)
    stream.flush()


def format_message(message, args):
    if args:
        return format_format_string(message, args)

    if not isinstance(message, str):
        return format_console_value(message)

    return decode_format_escapes(message)


def format_format_string(format_string, args):
    if not isinstance(format_string, str):
        raise ConsoleFormatError(
            "fprintf format string must be a string"
        )

    specifiers = parse_format_specifiers(format_string)

    if len(args) != len(specifiers):
        raise ConsoleFormatError(
            "fprintf expected "
            f"{len(specifiers)} argument(s), got {len(args)}"
        )

    decoded = decode_format_escapes(format_string)
    coerced_args = tuple(
        coerce_format_arg(arg, specifier)
        for arg, specifier in zip(args, specifiers)
    )

    try:
        return decoded % coerced_args
    except (TypeError, ValueError) as exc:
        raise ConsoleFormatError(
            f"fprintf format error: {exc}"
        ) from exc


def parse_format_specifiers(format_string):
    specifiers = []
    index = 0

    while index < len(format_string):
        if format_string[index] != "%":
            index += 1
            continue

        if index + 1 < len(format_string) and format_string[index + 1] == "%":
            index += 2
            continue

        index += 1

        while index < len(format_string) and format_string[index] in "-+0 #":
            index += 1

        while index < len(format_string) and format_string[index].isdigit():
            index += 1

        if index < len(format_string) and format_string[index] == ".":
            index += 1

            while index < len(format_string) and format_string[index].isdigit():
                index += 1

        if index >= len(format_string):
            raise ConsoleFormatError(
                "Incomplete fprintf format specifier"
            )

        specifier = format_string[index]

        if specifier not in {"s", "d", "i", "f"}:
            raise ConsoleFormatError(
                f"Unsupported fprintf format specifier '%{specifier}'"
            )

        specifiers.append(specifier)
        index += 1

    return specifiers


def coerce_format_arg(value, specifier):
    if isinstance(value, np.generic):
        value = value.item()

    if specifier == "s":
        return format_console_value(value)

    if specifier in {"d", "i"}:
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise ConsoleFormatError(
                f"%{specifier} requires an integer-compatible value"
            ) from exc

    if specifier == "f":
        try:
            return float(value)
        except (TypeError, ValueError) as exc:
            raise ConsoleFormatError(
                "%f requires a floating-point-compatible value"
            ) from exc

    return value


def decode_format_escapes(value):
    escapes = {
        "n": "\n",
        "r": "\r",
        "t": "\t",
        "\\": "\\",
        "'": "'",
        '"': '"',
    }

    result = []
    index = 0

    while index < len(value):
        char = value[index]

        if char != "\\" or index + 1 >= len(value):
            result.append(char)
            index += 1
            continue

        escaped = value[index + 1]
        result.append(escapes.get(escaped, escaped))
        index += 2

    return "".join(result)


def format_console_value(value):
    if value is None:
        return ""

    if isinstance(value, str):
        return value

    if isinstance(value, (bool, np.bool_)):
        return "true" if value else "false"

    if isinstance(value, np.generic):
        value = value.item()

    if isinstance(value, float):
        return format_number(value)

    if isinstance(value, (list, tuple, np.ndarray)):
        return format_console_array(value)

    if isinstance(value, dict):
        return format_value(value)

    return format_value(value)


def format_console_array(value):
    try:
        array = np.asarray(value)
    except ValueError:
        return "[" + ", ".join(
            format_console_value(item)
            for item in value
        ) + "]"

    if array.size == 0:
        return "[]"

    if array.ndim == 0:
        return format_console_value(array.item())

    if np.iscomplexobj(array):
        return format_value(array)

    return np.array2string(
        array,
        separator=" ",
        formatter={"all": format_array_cell},
    )


def format_array_cell(value):
    if isinstance(value, np.generic):
        value = value.item()

    if isinstance(value, (bool, np.bool_)):
        return "true" if value else "false"

    if isinstance(value, float):
        return format_number(value)

    return str(value)


def format_number(value):
    if abs(value) < 1e-12:
        value = 0.0

    return f"{value:g}"


if __name__ == "__main__":
    disp("Matrix output:")
    disp([[1, 2, 3], [4, 5, 6]])

    name = "Alice"
    count = 7
    pi_value = np.pi
    fprintf(
        "Hello %s, count=%d, pi=%.2f\n",
        name,
        count,
        pi_value,
    )

    warning(
        "Input %.1f is above the recommended limit of %d.",
        12.5,
        10,
    )

    try:
        error(
            "File '%s' was not found after %d attempt(s).",
            "data.csv",
            3,
        )
    except ConsoleAbortError as exc:
        fprintf("Caught expected error: %s\n", exc)
