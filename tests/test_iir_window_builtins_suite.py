import numpy as np


def test_butter_designs_coefficients_and_filters_signal(execute):
    _, context = execute(
        """
[b, a] = butter(4, 0.25);
x = [1 2 3 4 5 6 7 8 9 10];
y = filter(b, a, x);
nb = length(b);
na = length(a);
"""
    )

    assert context.variables["nb"] == 5
    assert context.variables["na"] == 5
    assert context.variables["y"].shape == (10,)
    assert np.all(np.isfinite(context.variables["y"]))


def test_iir_designers_support_common_forms(execute):
    _, context = execute(
        """
[b1, a1] = cheby1(4, 1, 0.3);
[b2, a2] = cheby2(4, 40, 0.3, "high");
[b3, a3] = ellip(4, 1, 40, [0.2 0.5], "bandpass");
[b4, a4] = butter(3, [0.2 0.5], "stop");
lens = [length(b1) length(a1) length(b2) length(a2) length(b3) length(a3) length(b4) length(a4)];
"""
    )

    np.testing.assert_array_equal(
        context.variables["lens"],
        np.array([5, 5, 5, 5, 9, 9, 7, 7]),
    )


def test_iir_analog_design_accepts_s_option(execute):
    _, context = execute(
        """
[b, a] = butter(3, 20, "s");
nb = length(b);
na = length(a);
"""
    )

    assert context.variables["nb"] >= 1
    assert context.variables["na"] == 4


def test_window_functions_return_column_vectors(execute):
    _, context = execute(
        """
w_hann = hann(8);
w_hamming = hamming(8, "periodic");
w_blackman = blackman(8, "symmetric", "single");
w_kaiser = kaiser(8, 5);
sizes = [size(w_hann, 1) size(w_hann, 2) size(w_hamming, 1) size(w_blackman, 1) size(w_kaiser, 1)];
"""
    )

    np.testing.assert_array_equal(
        context.variables["sizes"],
        np.array([8, 1, 8, 8, 8]),
    )
    assert context.variables["w_hann"][0, 0] == 0
    assert context.variables["w_hann"][-1, 0] == 0
    assert context.variables["w_hamming"][0, 0] > 0
    assert context.variables["w_kaiser"][4, 0] > context.variables["w_kaiser"][0, 0]
