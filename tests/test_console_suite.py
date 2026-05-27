import numpy as np
import pytest

from core.stdlib.console import (
    ConsoleAbortError,
    ConsoleFormatError,
    disp,
    error,
    fprintf,
    warning,
)


def test_disp_formats_matrix_and_appends_newline():
    output = []

    disp(
        np.array([[1, 2], [3, 4]]),
        output_callback=output.append,
    )

    assert output == ["[[1 2]\n [3 4]]\n\n"]


def test_fprintf_formats_strings_integers_and_float_precision():
    output = []

    fprintf(
        "Hello %s, count=%d, pi=%.2f",
        "Alice",
        7,
        np.pi,
        output_callback=output.append,
    )

    assert output == [
        "Hello Alice, count=7, pi=3.14"
    ]


def test_fprintf_rejects_missing_arguments():
    with pytest.raises(ConsoleFormatError) as raised:
        fprintf("%s %d", "only one")

    assert "expected 2 argument(s), got 1" in str(
        raised.value
    )


def test_warning_supports_fprintf_style_formatting():
    output = []

    warning(
        "Input %.1f exceeds limit %d",
        12.5,
        10,
        output_callback=output.append,
    )

    assert output == [
        "Warning: Input 12.5 exceeds limit 10\n"
    ]


def test_error_outputs_and_raises():
    output = []

    with pytest.raises(ConsoleAbortError) as raised:
        error(
            "File %s missing",
            "data.csv",
            output_callback=output.append,
        )

    assert output == [
        "Error: File data.csv missing\n"
    ]
    assert str(raised.value) == (
        "Error: File data.csv missing"
    )
    assert raised.value.already_reported is True
