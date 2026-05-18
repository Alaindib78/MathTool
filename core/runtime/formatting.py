import numpy as np


def format_value(value):
    if isinstance(value, dict):
        return format_struct(value)

    if isinstance(value, np.ndarray):
        return format_array(value)

    if isinstance(value, np.generic):
        value = value.item()

    if isinstance(value, complex):
        return format_complex(value)

    return str(value)


def format_struct(value):
    return "\n".join(
        f"{key}: {format_value(field_value)}"
        for key, field_value in value.items()
    )


def format_array(value):
    array = np.asarray(value)

    if array.ndim == 0:
        return format_value(array.item())

    if not np.iscomplexobj(array):
        return str(value)

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
            format_complex(cell)
            for cell in row
        )
        for row in rows
    )

    return f"{shape} complex\n\n{body}"


def format_complex(value):
    real = normalize_zero(float(value.real))
    imag = normalize_zero(float(value.imag))
    sign = "+" if imag >= 0 else "-"

    return (
        f"{real:.4f} {sign} "
        f"{abs(imag):.4f}i"
    )


def normalize_zero(value):
    if abs(value) < 1e-12:
        return 0.0

    return value
