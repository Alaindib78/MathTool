from __future__ import annotations

import numpy as np

from core.control.conversions import require_lti_model, to_transfer_function


def root_locus_data(model, gains=None):
    require_lti_model(model, "rlocus")
    tf_model = to_transfer_function(model)

    if gains is None:
        gains = default_gains(tf_model)
    else:
        gains = np.asarray(gains, dtype=float).reshape(-1)

    numerator = np.asarray(tf_model.numerator, dtype=complex)
    denominator = np.asarray(tf_model.denominator, dtype=complex)
    length = max(numerator.size, denominator.size)
    numerator = np.pad(numerator, (length - numerator.size, 0))
    denominator = np.pad(denominator, (length - denominator.size, 0))
    roots = []

    for gain in gains:
        roots.append(np.roots(denominator + gain * numerator))

    return np.asarray(roots), gains


def default_gains(tf_model):
    poles = np.roots(tf_model.denominator)
    scale = max(1.0, np.max(np.abs(poles)) if poles.size else 1.0)
    linear = np.linspace(0, 10 * scale, 120)
    logarithmic = np.logspace(-3, 3, 120) * scale
    return np.unique(np.concatenate([linear, logarithmic]))
