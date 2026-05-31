import math

import numpy as np

from core.errors.errors import RuntimeError as MathToolRuntimeError
from core.runtime.struct import MatlabStruct, is_struct


class DigitalFilter(MatlabStruct):
    """Small MATLAB-like digitalFilter object backed by coefficients."""

    def __init__(
        self,
        numerator,
        denominator=None,
        *,
        response="",
        sample_rate=2.0,
        method="",
        options=None,
    ):
        super().__init__()
        self["Numerator"] = np.asarray(numerator, dtype=float)
        self["Denominator"] = normalize_denominator(denominator)
        self["Response"] = response
        self["SampleRate"] = float(sample_rate)
        self["DesignMethod"] = method
        self["Options"] = MatlabStruct(options or {})

    @property
    def numerator(self):
        return self["Numerator"]

    @property
    def denominator(self):
        return self["Denominator"]

    def __str__(self):
        return (
            "digitalFilter with fields:\n"
            "    Numerator\n"
            "    Denominator\n"
            "    Response\n"
            "    SampleRate\n"
            "    DesignMethod"
        )


def lowpass_filter(x, cutoff, *arguments):
    return convenience_filter("lowpass", x, cutoff, *arguments)


def highpass_filter(x, cutoff, *arguments):
    return convenience_filter("highpass", x, cutoff, *arguments)


def bandpass_filter(x, passband, *arguments):
    return convenience_filter("bandpass", x, passband, *arguments)


def bandstop_filter(x, stopband, *arguments):
    return convenience_filter("bandstop", x, stopband, *arguments)


def convenience_filter(kind, x, cutoff, *arguments):
    signal = require_signal(x)
    positional, options = parse_name_value(arguments)

    sample_rate = 2.0
    if positional:
        sample_rate = positive_scalar(
            positional[0],
            f"{kind}: fs must be a positive scalar",
        )
        if len(positional) > 1:
            raise MathToolRuntimeError(
                f"{kind}: too many positional arguments"
            )

    impulse_response = str(
        option_value(options, "impulseresponse", "auto")
    ).lower()
    order = int(option_value(options, "filterorder", 0) or 0)

    if impulse_response not in {"auto", "fir", "iir"}:
        raise MathToolRuntimeError(
            f"{kind}: ImpulseResponse must be 'auto', 'fir', or 'iir'"
        )

    if impulse_response == "fir":
        if order <= 0:
            order = 64
        numerator = fir1(order, cutoff, filter_type_for_fir(kind), fs=sample_rate)
        filt = DigitalFilter(
            numerator,
            [1.0],
            response=f"{kind}fir",
            sample_rate=sample_rate,
            method="fir1",
            options=options,
        )
    else:
        if order <= 0:
            order = 8
        b, a = butter_design(kind, order, cutoff, sample_rate)
        filt = DigitalFilter(
            b,
            a,
            response=f"{kind}iir",
            sample_rate=sample_rate,
            method="butter",
            options=options,
        )

    return filtfilt_signal(filt, signal)


def design_filter(response, *arguments):
    response = str(response).lower()
    options = parse_name_value(arguments)[1]

    sample_rate = positive_scalar(
        option_value(options, "samplerate", 2.0),
        "designfilt: SampleRate must be positive",
    )
    order = int(option_value(options, "filterorder", 8))
    if order <= 0:
        raise MathToolRuntimeError(
            "designfilt: FilterOrder must be positive"
        )

    if response.endswith("fir"):
        kind = response[:-3]
        cutoff = cutoff_from_options(kind, options)
        numerator = fir1(
            order,
            cutoff,
            filter_type_for_fir(kind),
            fs=sample_rate,
        )
        return DigitalFilter(
            numerator,
            [1.0],
            response=response,
            sample_rate=sample_rate,
            method=str(option_value(options, "designmethod", "window")),
            options=options,
        )

    if response.endswith("iir"):
        kind = response[:-3]
        cutoff = cutoff_from_options(kind, options)
        b, a = butter_design(kind, order, cutoff, sample_rate)
        return DigitalFilter(
            b,
            a,
            response=response,
            sample_rate=sample_rate,
            method=str(option_value(options, "designmethod", "butter")),
            options=options,
        )

    raise MathToolRuntimeError(
        f"designfilt: unsupported response '{response}'"
    )


def filter_signal(*arguments):
    if len(arguments) < 2:
        raise MathToolRuntimeError(
            "filter expects filter(b, a, x) or filter(d, x)"
        )

    if is_filter_object(arguments[0]):
        if len(arguments) != 2:
            raise MathToolRuntimeError(
                "filter(d, x) expects exactly two arguments"
            )
        b, a = coefficients_from_filter(arguments[0])
        x = arguments[1]
    else:
        if len(arguments) not in {3, 4}:
            raise MathToolRuntimeError(
                "filter(b, a, x) expects numerator, denominator, and signal"
            )
        b = coefficient_vector(arguments[0], "filter: b")
        a = coefficient_vector(arguments[1], "filter: a")
        x = arguments[2]
        if len(arguments) == 4:
            raise MathToolRuntimeError(
                "filter: initial conditions are not currently supported"
            )

    signal_mod = require_scipy_signal("filter")
    return normalize_result(
        signal_mod.lfilter(
            b,
            a,
            require_signal(x),
            axis=signal_axis(x),
        )
    )


def filtfilt_signal(*arguments):
    if len(arguments) < 2:
        raise MathToolRuntimeError(
            "filtfilt expects filtfilt(b, a, x) or filtfilt(d, x)"
        )

    if is_filter_object(arguments[0]):
        if len(arguments) != 2:
            raise MathToolRuntimeError(
                "filtfilt(d, x) expects exactly two arguments"
            )
        b, a = coefficients_from_filter(arguments[0])
        x = arguments[1]
    else:
        if len(arguments) != 3:
            raise MathToolRuntimeError(
                "filtfilt(b, a, x) expects numerator, denominator, and signal"
            )
        b = coefficient_vector(arguments[0], "filtfilt: b")
        a = coefficient_vector(arguments[1], "filtfilt: a")
        x = arguments[2]

    signal_mod = require_scipy_signal("filtfilt")
    data = require_signal(x)
    axis = signal_axis(data)
    try:
        result = signal_mod.filtfilt(b, a, data, axis=axis)
    except ValueError:
        result = signal_mod.lfilter(b, a, data, axis=axis)
    return normalize_result(result)


def fir1(order, cutoff, ftype=None, window="hamming", scale=True, fs=2.0):
    signal_mod = require_scipy_signal("fir1")
    order = int(order)
    if order < 1:
        raise MathToolRuntimeError(
            "fir1: filter order must be positive"
        )

    cutoff_values = cutoff_vector(cutoff, fs, "fir1")
    pass_zero = pass_zero_for_fir(ftype, cutoff_values)

    try:
        return signal_mod.firwin(
            order + 1,
            cutoff_values,
            window=str(window).lower(),
            pass_zero=pass_zero,
            scale=bool(scale),
            fs=float(fs),
        )
    except ValueError as error:
        raise MathToolRuntimeError(
            f"fir1: {error}"
        ) from error


def butter_design(kind, order, cutoff, sample_rate):
    signal_mod = require_scipy_signal(kind)
    cutoff_values = cutoff_vector(cutoff, sample_rate, kind)
    if cutoff_values.size == 1:
        cutoff_values = float(cutoff_values[0])
    btype = {
        "lowpass": "lowpass",
        "highpass": "highpass",
        "bandpass": "bandpass",
        "bandstop": "bandstop",
    }.get(kind)
    if btype is None:
        raise MathToolRuntimeError(
            f"{kind}: unsupported filter type"
        )

    try:
        return signal_mod.butter(
            int(order),
            cutoff_values,
            btype=btype,
            fs=float(sample_rate),
        )
    except ValueError as error:
        raise MathToolRuntimeError(
            f"{kind}: {error}"
        ) from error


def cutoff_from_options(kind, options):
    if kind in {"lowpass", "highpass"}:
        for name in [
            "cutofffrequency",
            "halfpowerfrequency",
            "passbandfrequency",
            "stopbandfrequency",
        ]:
            value = option_value(options, name, None)
            if value is not None:
                return value
    else:
        first = None
        second = None
        for prefix in [
            "cutofffrequency",
            "halfpowerfrequency",
            "passbandfrequency",
            "stopbandfrequency",
        ]:
            first = option_value(options, prefix + "1", None)
            second = option_value(options, prefix + "2", None)
            if first is not None and second is not None:
                return [first, second]

    raise MathToolRuntimeError(
        f"designfilt: missing frequency constraints for {kind}"
    )


def filter_type_for_fir(kind):
    return {
        "lowpass": "low",
        "highpass": "high",
        "bandpass": "bandpass",
        "bandstop": "stop",
    }.get(kind, kind)


def pass_zero_for_fir(ftype, cutoff_values):
    if ftype is None:
        return cutoff_values.size == 1

    lowered = str(ftype).lower()
    if lowered in {"low", "lowpass"}:
        return True
    if lowered in {"high", "highpass"}:
        return False
    if lowered in {"bandpass", "pass"}:
        return False
    if lowered in {"stop", "bandstop", "notch"}:
        return True

    raise MathToolRuntimeError(
        f"fir1: unsupported filter type '{ftype}'"
    )


def cutoff_vector(value, sample_rate, function_name):
    try:
        cutoff = np.asarray(value, dtype=float).reshape(-1)
    except (TypeError, ValueError) as error:
        raise MathToolRuntimeError(
            f"{function_name}: cutoff frequency must be numeric"
        ) from error

    if cutoff.size not in {1, 2}:
        raise MathToolRuntimeError(
            f"{function_name}: cutoff must be a scalar or two-element vector"
        )

    nyquist = float(sample_rate) / 2.0
    if not np.all(np.isfinite(cutoff)) or np.any(cutoff <= 0) or np.any(cutoff >= nyquist):
        raise MathToolRuntimeError(
            f"{function_name}: cutoff frequencies must be between 0 and Nyquist"
        )

    if cutoff.size == 2 and cutoff[0] >= cutoff[1]:
        raise MathToolRuntimeError(
            f"{function_name}: cutoff frequencies must be increasing"
        )

    return cutoff


def coefficients_from_filter(value):
    return (
        coefficient_vector(value["Numerator"], "Numerator"),
        coefficient_vector(value["Denominator"], "Denominator"),
    )


def is_filter_object(value):
    return is_struct(value) and "Numerator" in value and "Denominator" in value


def coefficient_vector(value, label):
    try:
        coefficients = np.asarray(value, dtype=float).reshape(-1)
    except (TypeError, ValueError) as error:
        raise MathToolRuntimeError(
            f"{label} coefficients must be numeric"
        ) from error

    if coefficients.size == 0:
        raise MathToolRuntimeError(
            f"{label} coefficients must not be empty"
        )

    if not np.all(np.isfinite(coefficients)):
        raise MathToolRuntimeError(
            f"{label} coefficients must be finite"
        )

    if "denominator" in str(label).lower() and coefficients[0] == 0:
        raise MathToolRuntimeError(
            f"{label} first coefficient must be nonzero"
        )

    return coefficients


def normalize_denominator(value):
    if value is None:
        return np.array([1.0])
    return coefficient_vector(value, "Denominator")


def require_signal(value):
    try:
        data = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as error:
        raise MathToolRuntimeError(
            "filter input signal must be numeric"
        ) from error

    if data.size == 0:
        return data

    if np.iscomplexobj(data) or not np.all(np.isfinite(data)):
        raise MathToolRuntimeError(
            "filter input signal must contain finite real values"
        )

    return data


def signal_axis(value):
    array = np.asarray(value)
    if array.ndim <= 1:
        return -1
    return 0


def positive_scalar(value, message):
    try:
        scalar = float(np.asarray(value).item())
    except (TypeError, ValueError) as error:
        raise MathToolRuntimeError(message) from error

    if not math.isfinite(scalar) or scalar <= 0:
        raise MathToolRuntimeError(message)

    return scalar


def parse_name_value(arguments):
    positional = []
    options = {}
    index = 0
    arguments = list(arguments)

    while index < len(arguments):
        argument = arguments[index]

        if hasattr(argument, "name") and hasattr(argument, "value"):
            options[normalize_option_name(argument.name)] = argument.value
            index += 1
            continue

        if isinstance(argument, str) and index + 1 < len(arguments):
            options[normalize_option_name(argument)] = arguments[index + 1]
            index += 2
            continue

        positional.append(argument)
        index += 1

    return positional, options


def option_value(options, name, default):
    return options.get(normalize_option_name(name), default)


def normalize_option_name(name):
    return str(name).replace("_", "").replace(" ", "").lower()


def normalize_result(value):
    if isinstance(value, np.generic):
        return value.item()
    array = np.asarray(value)
    if array.ndim == 0:
        return array.item()
    return value


def require_scipy_signal(function_name):
    try:
        from scipy import signal
    except ImportError as error:
        raise MathToolRuntimeError(
            f"{function_name}: scipy.signal is required"
        ) from error

    return signal
