from __future__ import annotations

import numpy as np

from core.control.lti import is_lti_model, trim_leading_zeros
from core.control.state_space import StateSpaceModel
from core.control.transfer_function import TransferFunctionModel
from core.control.zero_pole_gain import ZeroPoleGainModel
from core.errors.errors import RuntimeError as MathToolRuntimeError


def require_scipy_signal():
    try:
        from scipy import signal
    except ImportError as error:
        raise MathToolRuntimeError(
            "control: scipy.signal is required for LTI conversions and analysis"
        ) from error

    return signal


def require_lti_model(value, function_name):
    if not is_lti_model(value):
        raise MathToolRuntimeError(
            f"{function_name}: expected LTI model, got {type(value).__name__}"
        )


def require_siso_state_space(model, function_name):
    if model.B.shape[1] != 1 or model.C.shape[0] != 1 or model.D.shape != (1, 1):
        raise MathToolRuntimeError(
            f"{function_name}: only SISO state-space conversion is currently supported"
        )


def metadata_from(model):
    return {
        "input_delay": model.input_delay,
        "output_delay": model.output_delay,
        "io_delay": model.io_delay,
        "name": model.name,
        "input_name": list(model.input_name),
        "output_name": list(model.output_name),
        "notes": list(model.notes),
        "user_data": model.user_data,
    }


def to_transfer_function(model):
    require_lti_model(model, "tf")

    if isinstance(model, TransferFunctionModel):
        return model

    signal = require_scipy_signal()

    if isinstance(model, StateSpaceModel):
        require_siso_state_space(model, "tf")
        try:
            numerator, denominator = signal.ss2tf(
                model.A,
                model.B,
                model.C,
                model.D,
            )
        except Exception as error:
            raise MathToolRuntimeError(f"tf: {error}") from error

        numerator = np.asarray(numerator)
        if numerator.ndim == 2:
            numerator = numerator[0]

        return TransferFunctionModel(
            trim_leading_zeros(numerator),
            trim_leading_zeros(denominator),
            model.Ts,
            **metadata_from(model),
        )

    if isinstance(model, ZeroPoleGainModel):
        try:
            numerator, denominator = signal.zpk2tf(
                model.zeros,
                model.poles,
                model.gain,
            )
        except Exception as error:
            raise MathToolRuntimeError(f"tf: {error}") from error

        return TransferFunctionModel(
            trim_leading_zeros(numerator),
            trim_leading_zeros(denominator),
            model.Ts,
            **metadata_from(model),
        )

    raise MathToolRuntimeError("tf: unsupported LTI model type")


def to_state_space(model):
    require_lti_model(model, "ss")

    if isinstance(model, StateSpaceModel):
        return model

    signal = require_scipy_signal()

    if isinstance(model, ZeroPoleGainModel):
        model = to_transfer_function(model)

    if isinstance(model, TransferFunctionModel):
        try:
            A, B, C, D = signal.tf2ss(
                model.numerator,
                model.denominator,
            )
        except Exception as error:
            raise MathToolRuntimeError(f"ss: {error}") from error

        return StateSpaceModel(
            A,
            B,
            C,
            D,
            model.Ts,
            **metadata_from(model),
        )

    raise MathToolRuntimeError("ss: unsupported LTI model type")


def to_zero_pole_gain(model):
    require_lti_model(model, "zpk")

    if isinstance(model, ZeroPoleGainModel):
        return model

    signal = require_scipy_signal()

    if isinstance(model, StateSpaceModel):
        model = to_transfer_function(model)

    if isinstance(model, TransferFunctionModel):
        try:
            zeros, poles, gain = signal.tf2zpk(
                model.numerator,
                model.denominator,
            )
        except Exception as error:
            raise MathToolRuntimeError(f"zpk: {error}") from error

        return ZeroPoleGainModel(
            zeros,
            poles,
            gain,
            model.Ts,
            **metadata_from(model),
        )

    raise MathToolRuntimeError("zpk: unsupported LTI model type")
