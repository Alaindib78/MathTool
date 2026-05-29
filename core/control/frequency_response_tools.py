from __future__ import annotations

import numpy as np

from core.control.response import bode_response, frequency_response


def bode_magnitude(model, w=None):
    frequency, magnitude_db, _ = bode_response(model, w)
    return frequency, magnitude_db


def nyquist_response(model, w=None):
    frequency, _, _ = bode_response(model, w)
    response = frequency_response(model, frequency)
    curve = np.concatenate([response, np.conj(response[::-1])])
    return np.real(curve), np.imag(curve)
