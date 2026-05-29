from __future__ import annotations

import numpy as np

from core.control.conversions import (
    require_lti_model,
    to_transfer_function,
)
from core.control.state_space import StateSpaceModel
from core.control.transfer_function import TransferFunctionModel
from core.control.zero_pole_gain import ZeroPoleGainModel


def poles(model):
    require_lti_model(model, "pole")

    if isinstance(model, StateSpaceModel):
        return np.linalg.eigvals(model.A)

    if isinstance(model, TransferFunctionModel):
        return np.roots(model.denominator)

    if isinstance(model, ZeroPoleGainModel):
        return model.poles

    return np.roots(to_transfer_function(model).denominator)


def zeros(model):
    require_lti_model(model, "zero")

    if isinstance(model, TransferFunctionModel):
        return np.roots(model.numerator)

    if isinstance(model, ZeroPoleGainModel):
        return model.zeros

    return np.roots(to_transfer_function(model).numerator)
