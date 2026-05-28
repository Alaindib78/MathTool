import re

import numpy as np

from core.errors.errors import LexerError


INTEGER_SUFFIX_TYPES = {
    "u8": (np.uint8, 8, False),
    "u16": (np.uint16, 16, False),
    "u32": (np.uint32, 32, False),
    "u64": (np.uint64, 64, False),
    "s8": (np.int8, 8, True),
    "s16": (np.int16, 16, True),
    "s32": (np.int32, 32, True),
    "s64": (np.int64, 64, True),
}

INTEGER_SUFFIX_RE = re.compile(r"([us]\d+)$")


def parse_numeric_literal(text, line, column):
    if len(text) < 2:
        raise invalid_literal("numeric", text, line, column)

    prefix = text[:2].lower()

    if prefix == "0x":
        return parse_hex_literal(text, line, column)

    if prefix == "0b":
        return parse_binary_literal(text, line, column)

    raise invalid_literal("numeric", text, line, column)


def parse_hex_literal(text, line, column):
    digits, suffix = parse_integer_suffix(
        text[2:],
        "hexadecimal",
        text,
        line,
        column,
    )

    if not digits or any(char not in "0123456789abcdefABCDEF" for char in digits):
        raise invalid_literal("hexadecimal", text, line, column)

    value = int(digits, 16)
    return apply_integer_suffix(value, suffix, text, line, column)


def parse_binary_literal(text, line, column):
    digits, suffix = parse_integer_suffix(
        text[2:],
        "binary",
        text,
        line,
        column,
    )

    if not digits or any(char not in "01" for char in digits):
        raise invalid_literal("binary", text, line, column)

    value = int(digits, 2)
    return apply_integer_suffix(value, suffix, text, line, column)


def parse_integer_suffix(body, literal_kind, text, line, column):
    match = INTEGER_SUFFIX_RE.search(body)

    if match is None:
        return body, None

    suffix = match.group(1)

    if suffix not in INTEGER_SUFFIX_TYPES:
        raise LexerError(
            f"Invalid {literal_kind} literal '{text}': "
            f"unsupported integer suffix '{suffix}'",
            line=line,
            column=column,
            token=text,
        )

    return body[: match.start()], suffix


def apply_integer_suffix(value, suffix, text, line, column):
    if suffix is None:
        return value

    numpy_type, bits, signed = INTEGER_SUFFIX_TYPES[suffix]
    max_raw_value = 2**bits - 1

    if value > max_raw_value:
        raise LexerError(
            f"Invalid integer literal '{text}': value does not fit "
            f"in {bits} bits",
            line=line,
            column=column,
            token=text,
        )

    if signed and value >= 2 ** (bits - 1):
        value -= 2**bits

    return numpy_type(value)


def invalid_literal(literal_kind, text, line, column):
    return LexerError(
        f"Invalid {literal_kind} literal '{text}'",
        line=line,
        column=column,
        token=text,
    )
