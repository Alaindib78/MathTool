import numpy as np
import pytest

from core.errors.errors import RuntimeError as MathToolRuntimeError


def test_filter_applies_coefficient_form(execute):
    _, context = execute(
        """
x = [1 3 5];
y = filter([1 1]/2, 1, x);
"""
    )

    np.testing.assert_allclose(
        context.variables["y"],
        np.array([0.5, 2.0, 4.0]),
        atol=1e-12,
    )


def test_fir1_designs_expected_number_of_coefficients(execute):
    _, context = execute(
        """
b = fir1(20, 0.4);
n = length(b);
"""
    )

    assert context.variables["n"] == 21
    assert np.all(np.isfinite(context.variables["b"]))


def test_designfilt_returns_filter_object_and_filter_accepts_it(execute):
    _, context = execute(
        """
d = designfilt("lowpassfir", "FilterOrder", 12, "CutoffFrequency", 0.35);
num = d.Numerator;
den = d.Denominator;
y = filter(d, [1 2 3 4 5]);
"""
    )

    assert len(context.variables["num"]) == 13
    np.testing.assert_allclose(context.variables["den"], np.array([1.0]))
    assert context.variables["y"].shape == (5,)


def test_filtfilt_preserves_signal_shape(execute):
    _, context = execute(
        """
x = [1 2 3 2 1 0 -1 0 1 2 3 2 1];
b = fir1(4, 0.5);
y = filtfilt(b, 1, x);
"""
    )

    assert context.variables["y"].shape == context.variables["x"].shape
    assert np.all(np.isfinite(context.variables["y"]))


def test_lowpass_and_highpass_filter_signals(execute):
    _, context = execute(
        """
fs = 100;
t = 0:1/fs:1;
x_low = sin(2*pi*5*t);
x_high = 0.5*sin(2*pi*30*t);
x = x_low + x_high;
y_low = lowpass(x, 10, fs, "FilterOrder", 4);
y_high = highpass(x, 20, fs, "FilterOrder", 4);
low_error = mean(abs(y_low - x_low));
high_error = mean(abs(y_high - x_high));
"""
    )

    assert context.variables["low_error"] < 0.25
    assert context.variables["high_error"] < 0.25


def test_bandpass_and_bandstop_filter_signals(execute):
    _, context = execute(
        """
fs = 100;
t = 0:1/fs:1;
x5 = sin(2*pi*5*t);
x20 = sin(2*pi*20*t);
x = x5 + x20;
y_band = bandpass(x, [15 25], fs, "FilterOrder", 4);
y_stop = bandstop(x, [15 25], fs, "FilterOrder", 4);
band_error = mean(abs(y_band - x20));
stop_error = mean(abs(y_stop - x5));
"""
    )

    assert context.variables["band_error"] < 0.35
    assert context.variables["stop_error"] < 0.35


def test_filter_rejects_invalid_cutoff(execute):
    with pytest.raises(MathToolRuntimeError, match="cutoff"):
        execute(
            """
x = [1 2 3];
y = lowpass(x, 2);
"""
        )
