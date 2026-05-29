from __future__ import annotations

import numpy as np

from core.control.response import bode_response


def stability_margins(model, w=None):
    frequency, magnitude_db, phase_deg = bode_response(model, w)
    phase_unwrapped = np.unwrap(np.deg2rad(phase_deg)) * 180 / np.pi
    magnitude_abs = 10 ** (magnitude_db / 20)

    wcp = crossing_frequency(frequency, magnitude_db, 0.0)
    pm = np.inf
    if np.isfinite(wcp):
        phase_at_wcp = np.interp(wcp, frequency, phase_unwrapped)
        pm = 180.0 + phase_at_wcp

    phase_cross = phase_unwrapped + 180.0
    wcg = crossing_frequency(frequency, phase_cross, 0.0)
    gm = np.inf
    if np.isfinite(wcg):
        mag_at_wcg = np.interp(wcg, frequency, magnitude_abs)
        if not np.isclose(mag_at_wcg, 0):
            gm = 1.0 / mag_at_wcg

    return {
        "GainMargin": float(np.real_if_close(gm)),
        "PhaseMargin": float(np.real_if_close(pm)),
        "GMFrequency": float(np.real_if_close(wcg)),
        "PMFrequency": float(np.real_if_close(wcp)),
    }


def crossing_frequency(x, y, target):
    values = np.asarray(y, dtype=float) - target
    signs = np.sign(values)

    for index in range(len(values) - 1):
        if np.isclose(values[index], 0):
            return float(x[index])

        if signs[index] == 0:
            return float(x[index])

        if signs[index] * signs[index + 1] < 0:
            x0, x1 = x[index], x[index + 1]
            y0, y1 = values[index], values[index + 1]

            if np.isclose(y1, y0):
                return float(x0)

            return float(x0 + (target - y0) * (x1 - x0) / (y1 - y0))

    return float("nan")
