import math
import numpy as np
import sympy as sp

from core.errors.errors import RuntimeError as MathToolRuntimeError
from core.runtime.symbolic import (
    NameValueOption,
    SymbolicEquation,
    SymbolicValue,
    as_sequence,
    from_sympy_equation,
    from_sympy_value,
    is_symbolic,
    symbol_from_variable,
    symbol_sort_key,
    sympy_symbols_for,
    to_sympy_equation,
    to_sympy_expression,
)
from core.runtime.struct import MatlabStruct
from core.stdlib.console import (
    disp,
    error as console_error,
    fprintf,
    warning,
)


def builtin_disp(context, *args):
    if len(args) != 1:
        raise Exception(
            "disp expects exactly 1 argument"
        )

    disp(
        args[0],
        output_callback=context.output_callback,
    )

    return None


def builtin_fprintf(context, format_string, *args):
    fprintf(
        format_string,
        *args,
        output_callback=context.output_callback,
    )

    return None


def builtin_warning(context, message, *args):
    warning(
        message,
        *args,
        output_callback=context.output_callback,
    )

    return None


def builtin_error(context, message, *args):
    console_error(
        message,
        *args,
        output_callback=context.output_callback,
    )


def builtin_help(context, topic=None):
    text = context.help_database.format_help(topic)

    if context.output_callback is not None:
        context.output_callback(text + "\n")
        return None

    return text


def builtin_lookfor(context, keyword):
    text = context.help_database.format_lookfor(keyword)

    if context.output_callback is not None:
        context.output_callback(text + "\n")
        return None

    return text


def builtin_cwd(context):
    return context.current_working_directory


def builtin_who(context):
    return context.who()


def builtin_struct(context, *arguments):
    if len(arguments) % 2 != 0:
        raise MathToolRuntimeError(
            "struct expects name/value pairs"
        )

    result = MatlabStruct()

    for index in range(0, len(arguments), 2):
        field_name = arguments[index]

        if not isinstance(field_name, str):
            raise MathToolRuntimeError(
                "struct field names must be strings"
            )

        result[field_name] = arguments[index + 1]

    return result


def builtin_sin(context,x):
    return np.sin(x)


def builtin_cos(context,x):
    return np.cos(x)


def builtin_tan(context,x):
    return np.tan(x)

def builtin_asin(context,x):
    return np.arcsin(x)


def builtin_acos(context,x):
    return np.arccos(x)


def builtin_atan(context,x):
    return np.arctan(x)


def builtin_atan2(context, y, x):
    return np.arctan2(y, x)


def builtin_sinh(context, x):
    return np.sinh(x)


def builtin_cosh(context, x):
    return np.cosh(x)


def builtin_tanh(context, x):
    return np.tanh(x)


def builtin_asinh(context, x):
    return np.arcsinh(x)


def builtin_acosh(context, x):
    return np.arccosh(x)


def builtin_atanh(context, x):
    return np.arctanh(x)

def builtin_log(context,x):
    return np.log(x)

def builtin_log10(context,x):
    return np.log10(x)


def builtin_log2(context, x):
    return np.log2(x)


def builtin_exp(context,x):
    return np.exp(x)


def builtin_expm1(context, x):
    return np.expm1(x)


def builtin_sqrt(context,x):
    array = np.asarray(x)

    if (
        not np.iscomplexobj(array)
        and np.any(array < 0)
    ):
        result = np.sqrt(
            array.astype(complex)
        )

        if np.asarray(result).ndim == 0:
            return result.item()

        return result

    return np.sqrt(x)


def builtin_angle(context, z):
    return np.angle(z)


def builtin_conj(context, z):
    return np.conj(z)


def builtin_imag(context, z):
    return np.imag(z)


def builtin_isreal(context, z):
    return np.isrealobj(z)


def builtin_real(context, z):
    return np.real(z)


def builtin_abs(context,x):
    return np.abs(x)

def builtin_floor(context,x):
    return np.floor(x)

def builtin_ceil(context,x):
    return np.ceil(x)

def builtin_round(context, x, decimals=0):
    return np.round(x, int(decimals))


def builtin_fix(context, x):
    return np.fix(x)


def builtin_clip(context, x, lower, upper):
    return np.clip(x, lower, upper)


def builtin_deg2rad(context, x):
    return np.deg2rad(x)


def builtin_rad2deg(context, x):
    return np.rad2deg(x)

def builtin_sign(context,x):
    return np.sign(x)

def _as_array(value):
    return np.asarray(value)


def _normalize_result(value):
    if isinstance(value, np.generic):
        return value.item()

    array = np.asarray(value)

    if array.ndim == 0:
        return array.item()

    return value


def _axis_from_dim(dim):
    axis = int(dim) - 1

    if axis < 0:
        raise Exception("Dimension must be positive")

    return axis


def _shape_from_dimensions(
    dimensions,
    *,
    square_single_scalar=False,
):
    if len(dimensions) == 1:
        first = dimensions[0]

        if isinstance(first, np.ndarray):
            values = first.flatten().tolist()
        elif isinstance(first, (list, tuple)):
            values = list(first)
        else:
            value = int(first)

            if square_single_scalar:
                return (value, value)

            return (value,)

        return tuple(int(value) for value in values)

    return tuple(int(value) for value in dimensions)


def _first_nonsingleton_axis(array):
    for axis, size in enumerate(array.shape):
        if size > 1:
            return axis

    return 0


def _random_generator(context):
    if not hasattr(context, "random_generator"):
        context.random_generator = np.random.default_rng()

    return context.random_generator


def builtin_zeros(context, *dimensions):
    shape = _shape_from_dimensions(
        dimensions,
        square_single_scalar=True,
    )

    return np.zeros(shape)


def builtin_ones(context, *dimensions):
    shape = _shape_from_dimensions(
        dimensions,
        square_single_scalar=True,
    )

    return np.ones(shape)


def builtin_true(context, *dimensions):
    shape = _shape_from_dimensions(
        dimensions,
        square_single_scalar=True,
    )

    return _normalize_result(
        np.ones(shape, dtype=bool)
    )


def builtin_false(context, *dimensions):
    shape = _shape_from_dimensions(
        dimensions,
        square_single_scalar=True,
    )

    return _normalize_result(
        np.zeros(shape, dtype=bool)
    )


def builtin_eye(context, rows, cols=None):
    rows = int(rows)

    if cols is None:
        return np.eye(rows)

    return np.eye(rows, int(cols))


def builtin_det(context, value):
    array = _as_array(value)

    try:
        return float(np.round(np.linalg.det(array), 12))
    except np.linalg.LinAlgError as error:
        raise Exception(str(error))


def builtin_inv(context, value):
    array = _as_array(value)

    try:
        return np.linalg.inv(array)
    except np.linalg.LinAlgError as error:
        raise Exception(str(error))


def builtin_size(context, value, dim=None):
    array = _as_array(value)

    if dim is not None:
        axis = _axis_from_dim(dim)

        if array.ndim == 0:
            return 1 if axis == 0 else 1

        if axis >= array.ndim:
            return 1

        return int(array.shape[axis])

    if array.ndim == 0:
        return np.array([1, 1])

    return np.array(array.shape)


def builtin_sum(context, value, dim=None):
    array = _as_array(value)

    if dim is None:
        return _normalize_result(np.sum(array))

    return _normalize_result(
        np.sum(array, axis=_axis_from_dim(dim))
    )


def builtin_mean(context, value, dim=None):
    array = _as_array(value)

    if dim is None:
        return _normalize_result(np.mean(array))

    return _normalize_result(
        np.mean(array, axis=_axis_from_dim(dim))
    )


def builtin_max(context, value, dim=None):
    array = _as_array(value)

    if dim is None:
        return _normalize_result(np.max(array))

    return _normalize_result(
        np.max(array, axis=_axis_from_dim(dim))
    )


def builtin_min(context, value, dim=None):
    array = _as_array(value)

    if dim is None:
        return _normalize_result(np.min(array))

    return _normalize_result(
        np.min(array, axis=_axis_from_dim(dim))
    )


def builtin_length(context,x):
    array = _as_array(x)

    if array.ndim == 0:
        return 1

    return int(max(array.shape))


def builtin_numel(context, value):
    return int(_as_array(value).size)


def builtin_ndims(context, value):
    return int(_as_array(value).ndim)


def builtin_isempty(context, value):
    return bool(_as_array(value).size == 0)


def builtin_linspace(context, start, stop, num=100):
    return np.linspace(start, stop, int(num))


def builtin_logspace(context, start, stop, num=50):
    return np.logspace(start, stop, int(num))


def builtin_arange(context, start, stop=None, step=1):
    if stop is None:
        return np.arange(start)

    return np.arange(start, stop, step)


def builtin_zeros_like(context, value):
    return np.zeros_like(_as_array(value))


def builtin_ones_like(context, value):
    return np.ones_like(_as_array(value))


def builtin_rand(context, *dimensions):
    shape = _shape_from_dimensions(
        dimensions,
        square_single_scalar=True,
    )

    result = _random_generator(context).random(shape)

    return _normalize_result(result)


def builtin_randn(context, *dimensions):
    shape = _shape_from_dimensions(
        dimensions,
        square_single_scalar=True,
    )

    result = _random_generator(context).standard_normal(shape)

    return _normalize_result(result)


def builtin_randi(context, high, *dimensions):
    shape = _shape_from_dimensions(
        dimensions,
        square_single_scalar=True,
    )

    result = _random_generator(context).integers(
        1,
        int(high) + 1,
        size=shape if shape else None,
    )

    return _normalize_result(result)


def builtin_rng(context, seed=None):
    if seed is None:
        context.random_generator = np.random.default_rng()
    else:
        context.random_generator = np.random.default_rng(
            int(seed)
        )

    return None


def builtin_reshape(context, value, *dimensions):
    shape = _shape_from_dimensions(dimensions)

    return np.reshape(_as_array(value), shape)


def builtin_transpose(context, value):
    return np.transpose(_as_array(value))


def builtin_flatten(context, value):
    return _as_array(value).flatten()


def builtin_diag(context, value, k=0):
    return np.diag(_as_array(value), int(k))


def builtin_tril(context, value, k=0):
    return np.tril(_as_array(value), int(k))


def builtin_triu(context, value, k=0):
    return np.triu(_as_array(value), int(k))


def builtin_sort(context, value, dim=None):
    axis = -1 if dim is None else _axis_from_dim(dim)

    return np.sort(_as_array(value), axis=axis)


def builtin_unique(context, value):
    return np.unique(_as_array(value))


def builtin_find(context, value):
    return np.flatnonzero(_as_array(value)) + 1


def builtin_prod(context, value, dim=None):
    array = _as_array(value)

    if dim is None:
        return _normalize_result(np.prod(array))

    return _normalize_result(
        np.prod(array, axis=_axis_from_dim(dim))
    )


def builtin_median(context, value, dim=None):
    array = _as_array(value)

    if dim is None:
        return _normalize_result(np.median(array))

    return _normalize_result(
        np.median(array, axis=_axis_from_dim(dim))
    )


def builtin_std(context, value, dim=None, ddof=0):
    array = _as_array(value)

    if dim is None:
        return _normalize_result(
            np.std(array, ddof=int(ddof))
        )

    return _normalize_result(
        np.std(
            array,
            axis=_axis_from_dim(dim),
            ddof=int(ddof),
        )
    )


def builtin_var(context, value, dim=None, ddof=0):
    array = _as_array(value)

    if dim is None:
        return _normalize_result(
            np.var(array, ddof=int(ddof))
        )

    return _normalize_result(
        np.var(
            array,
            axis=_axis_from_dim(dim),
            ddof=int(ddof),
        )
    )


def builtin_percentile(context, value, q, dim=None):
    array = _as_array(value)

    if dim is None:
        return _normalize_result(np.percentile(array, q))

    return _normalize_result(
        np.percentile(
            array,
            q,
            axis=_axis_from_dim(dim),
        )
    )


def builtin_any(context, value, dim=None):
    array = _as_array(value)

    if dim is None:
        return bool(np.any(array))

    return np.any(array, axis=_axis_from_dim(dim))


def builtin_all(context, value, dim=None):
    array = _as_array(value)

    if dim is None:
        return bool(np.all(array))

    return np.all(array, axis=_axis_from_dim(dim))


def builtin_isnan(context, value):
    return np.isnan(value)


def builtin_isinf(context, value):
    return np.isinf(value)


def builtin_isfinite(context, value):
    return np.isfinite(value)


def builtin_isclose(context, a, b, rtol=1e-05, atol=1e-08):
    return np.isclose(a, b, rtol=rtol, atol=atol)


def builtin_allclose(context, a, b, rtol=1e-05, atol=1e-08):
    return bool(np.allclose(a, b, rtol=rtol, atol=atol))


def builtin_diff(context, value, n=1, dim=None):
    array = _as_array(value)
    axis = (
        _first_nonsingleton_axis(array)
        if dim is None
        else _axis_from_dim(dim)
    )

    return np.diff(array, n=int(n), axis=axis)


def builtin_gradient(context, value):
    result = np.gradient(_as_array(value))

    if isinstance(result, list):
        return np.array(result)

    return result


def builtin_cumsum(context, value, dim=None):
    array = _as_array(value)
    axis = None if dim is None else _axis_from_dim(dim)

    return _normalize_result(np.cumsum(array, axis=axis))


def builtin_cumprod(context, value, dim=None):
    array = _as_array(value)
    axis = None if dim is None else _axis_from_dim(dim)

    return _normalize_result(np.cumprod(array, axis=axis))


def builtin_trapz(context, x, y=None):
    if y is None:
        return _normalize_result(
            np.trapezoid(_as_array(x))
        )

    return _normalize_result(
        np.trapezoid(
            _as_array(y),
            _as_array(x),
        )
    )


def builtin_interp1(context, x, y, query):
    return _normalize_result(
        np.interp(
            query,
            _as_array(x),
            _as_array(y),
        )
    )


def builtin_dot(context, a, b):
    return _normalize_result(np.dot(a, b))


def builtin_cross(context, a, b):
    return np.cross(a, b)


def builtin_norm(context, value, order=None):
    if order is None:
        return _normalize_result(
            np.linalg.norm(_as_array(value))
        )

    return _normalize_result(
        np.linalg.norm(_as_array(value), order)
    )


def builtin_trace(context, value):
    return _normalize_result(np.trace(_as_array(value)))


def builtin_rank(context, value):
    return int(np.linalg.matrix_rank(_as_array(value)))


def builtin_cond(context, value):
    return _normalize_result(np.linalg.cond(_as_array(value)))


def builtin_pinv(context, value):
    return np.linalg.pinv(_as_array(value))


def builtin_linsolve(context, coefficients, constants):
    try:
        return _normalize_result(
            np.linalg.solve(
                _as_array(coefficients),
                _as_array(constants),
            )
        )
    except np.linalg.LinAlgError as error:
        raise Exception(str(error))


def builtin_eig(context, value):
    try:
        values, vectors = np.linalg.eig(_as_array(value))
    except np.linalg.LinAlgError as error:
        raise Exception(str(error))

    return {
        "values": values,
        "vectors": vectors,
    }


def builtin_svd(context, value):
    try:
        u, singular_values, vt = np.linalg.svd(
            _as_array(value)
        )
    except np.linalg.LinAlgError as error:
        raise Exception(str(error))

    return {
        "U": u,
        "S": singular_values,
        "Vt": vt,
    }


def builtin_qr(context, value):
    try:
        q, r = np.linalg.qr(_as_array(value))
    except np.linalg.LinAlgError as error:
        raise Exception(str(error))

    return {
        "Q": q,
        "R": r,
    }


def builtin_fft(context, value, n=None):
    if n is None:
        return np.fft.fft(_as_array(value))

    return np.fft.fft(_as_array(value), int(n))


def builtin_ifft(context, value, n=None):
    if n is None:
        return np.fft.ifft(_as_array(value))

    return np.fft.ifft(_as_array(value), int(n))


def builtin_fftshift(context, value):
    return np.fft.fftshift(_as_array(value))


def builtin_ifftshift(context, value):
    return np.fft.ifftshift(_as_array(value))


def builtin_fftfreq(context, n, d=1.0):
    return np.fft.fftfreq(int(n), float(d))


def builtin_roots(context, coefficients):
    return np.roots(_as_array(coefficients))


def builtin_polyval(context, coefficients, x):
    return _normalize_result(
        np.polyval(_as_array(coefficients), x)
    )


def builtin_polyfit(context, x, y, degree):
    return np.polyfit(
        _as_array(x),
        _as_array(y),
        int(degree),
    )


def builtin_conv(context, a, b):
    return np.convolve(_as_array(a), _as_array(b))


def _polynomial_coefficients(function_name, argument_name, value):
    try:
        coefficients = np.asarray(
            value,
            dtype=complex,
        ).reshape(-1)
    except (TypeError, ValueError) as error:
        raise Exception(
            f"{function_name}: {argument_name} must be a numeric "
            "coefficient vector"
        ) from error

    if coefficients.size == 0:
        raise Exception(
            f"{function_name}: {argument_name} must contain at least "
            "one coefficient"
        )

    if not np.all(np.isfinite(coefficients)):
        raise Exception(
            f"{function_name}: {argument_name} coefficients must be finite"
        )

    return coefficients


def _validate_transfer_function(function_name, numerator, denominator):
    num = _polynomial_coefficients(
        function_name,
        "numerator",
        numerator,
    )
    den = _polynomial_coefficients(
        function_name,
        "denominator",
        denominator,
    )

    if np.all(den == 0):
        raise Exception(
            f"{function_name}: denominator must not be the zero polynomial"
        )

    return num, den


def _frequency_vector(function_name, value, *, allow_zero=False):
    try:
        frequency = np.asarray(
            value,
            dtype=float,
        ).reshape(-1)
    except (TypeError, ValueError) as error:
        raise Exception(
            f"{function_name}: frequency must be a numeric vector"
        ) from error

    if frequency.size == 0:
        raise Exception(
            f"{function_name}: frequency must contain at least one value"
        )

    if not np.all(np.isfinite(frequency)):
        raise Exception(
            f"{function_name}: frequency values must be finite"
        )

    lower_bound_ok = (
        frequency >= 0
        if allow_zero
        else frequency > 0
    )

    if not np.all(lower_bound_ok):
        qualifier = "nonnegative" if allow_zero else "positive"
        raise Exception(
            f"{function_name}: frequency values must be {qualifier}"
        )

    return frequency


def _nonzero_finite_root_magnitudes(*polynomials):
    magnitudes = []

    for coefficients in polynomials:
        trimmed = np.trim_zeros(
            coefficients,
            trim="f",
        )

        if trimmed.size <= 1:
            continue

        roots = np.roots(trimmed)

        for value in np.abs(roots):
            if np.isfinite(value) and value > 0:
                magnitudes.append(value)

    return np.asarray(magnitudes, dtype=float)


def _default_frequency_vector(num, den):
    magnitudes = _nonzero_finite_root_magnitudes(
        num,
        den,
    )

    if magnitudes.size == 0:
        low_exp = -2
        high_exp = 2
    else:
        low_exp = int(
            np.floor(np.log10(np.min(magnitudes)))
        ) - 2
        high_exp = int(
            np.ceil(np.log10(np.max(magnitudes)))
        ) + 2

    low_exp = max(low_exp, -12)
    high_exp = min(high_exp, 12)

    if low_exp >= high_exp:
        low_exp -= 1
        high_exp += 1

    return np.logspace(low_exp, high_exp, 300)


def _transfer_response(num, den, frequency):
    s = 1j * frequency

    with np.errstate(divide="ignore", invalid="ignore"):
        return np.polyval(num, s) / np.polyval(den, s)


def _plot_bode_fallback(context, frequency, magnitude_db, phase_deg):
    x_values = np.log10(frequency)

    context.plot_engine.figure()
    context.plot_engine.plot(x_values, magnitude_db)
    context.plot_engine.title("Bode Diagram - Magnitude")
    context.plot_engine.xlabel("log10 Frequency (rad/s)")
    context.plot_engine.ylabel("Magnitude (dB)")
    context.plot_engine.grid_on()

    context.plot_engine.figure()
    context.plot_engine.plot(x_values, phase_deg)
    context.plot_engine.title("Bode Diagram - Phase")
    context.plot_engine.xlabel("log10 Frequency (rad/s)")
    context.plot_engine.ylabel("Phase (deg)")
    context.plot_engine.grid_on()


def _plot_nyquist_fallback(context, real_values, imag_values):
    context.plot_engine.figure()
    context.plot_engine.plot(real_values, imag_values)
    context.plot_engine.title("Nyquist Diagram")
    context.plot_engine.xlabel("Real")
    context.plot_engine.ylabel("Imaginary")
    context.plot_engine.grid_on()


def builtin_bode(context, numerator, denominator, frequency=None):
    num, den = _validate_transfer_function(
        "bode",
        numerator,
        denominator,
    )

    if frequency is None:
        frequency = _default_frequency_vector(num, den)
    else:
        frequency = _frequency_vector(
            "bode",
            frequency,
        )

    response = _transfer_response(
        num,
        den,
        frequency,
    )
    magnitude_db = 20 * np.log10(np.abs(response))
    phase_deg = np.rad2deg(
        np.unwrap(np.angle(response))
    )

    if hasattr(context.plot_engine, "bode"):
        context.plot_engine.bode(
            frequency,
            magnitude_db,
            phase_deg,
        )
    else:
        _plot_bode_fallback(
            context,
            frequency,
            magnitude_db,
            phase_deg,
        )

    return None


def builtin_nyquist(context, numerator, denominator, frequency=None):
    num, den = _validate_transfer_function(
        "nyquist",
        numerator,
        denominator,
    )

    if frequency is None:
        frequency = _default_frequency_vector(num, den)
    else:
        frequency = _frequency_vector(
            "nyquist",
            frequency,
            allow_zero=True,
        )

    response = _transfer_response(
        num,
        den,
        frequency,
    )
    curve = np.concatenate(
        [
            response,
            np.conj(response[::-1]),
        ]
    )

    real_values = np.real(curve)
    imag_values = np.imag(curve)

    if hasattr(context.plot_engine, "nyquist"):
        context.plot_engine.nyquist(
            real_values,
            imag_values,
        )
    else:
        _plot_nyquist_fallback(
            context,
            real_values,
            imag_values,
        )

    return None

def builtin_plot(context, x, y):
    context.plot_engine.plot(x, y)

def builtin_figure(context, number=None):
    context.plot_engine.figure(number)

    return None

def builtin_close(context, target=None):
    if isinstance(target, str):
        target = target.lower()

    context.plot_engine.close(target)

    return None

def builtin_mod(context, a, b):
    return np.mod(a, b)

def builtin_title(context, text):
    context.plot_engine.title(text)


def builtin_xlabel(context, text):
    context.plot_engine.xlabel(text)


def builtin_ylabel(context, text):
    context.plot_engine.ylabel(text)


def builtin_grid(context, value=True):
    if value:
        context.plot_engine.grid_on()
    else:
        context.plot_engine.grid_off()


def builtin_sym(context, value):
    if isinstance(value, SymbolicValue):
        return value

    return SymbolicValue(value)


def builtin_complex(context, real, imag=None):
    if imag is None:
        result = np.asarray(real, dtype=complex)
    else:
        result = (
            np.asarray(real)
            + 1j * np.asarray(imag)
        )

    if result.ndim == 0:
        return result.item()

    return result


def builtin_symvar(context, value):
    symbols = sympy_symbols_for(value)

    return np.array(
        [
            SymbolicValue(symbol.name)
            for symbol in symbols
        ],
        dtype=object,
    )


def builtin_solve(context, *arguments):
    positional, options = split_name_value_options(
        arguments
    )

    if not positional:
        raise Exception(
            "solve requires at least one equation"
        )

    equations = as_sequence(positional[0])
    variables = None

    if len(positional) >= 2:
        variables = [
            symbol_from_variable(value)
            for value in as_sequence(positional[1])
        ]
    else:
        symbols = sympy_symbols_for(equations)

        if len(equations) == 1:
            variables = [preferred_symbol(symbols)]
        else:
            variables = symbols

    if len(positional) > 2:
        raise Exception(
            "solve accepts equations, variables, and Name=Value options"
        )

    real_only = bool(
        options.get("real", False)
    )

    sympy_equations = [
        to_sympy_equation(equation)
        for equation in equations
    ]

    if len(variables) == 1:
        solutions = sp.solve(
            sympy_equations[0]
            if len(sympy_equations) == 1
            else sympy_equations,
            variables[0],
        )

        if real_only:
            solutions = [
                solution
                for solution in solutions
                if is_real_solution(solution)
            ]

        return converted_solution_list(
            solutions
        )

    solutions = sp.solve(
        sympy_equations,
        variables,
        dict=True,
    )

    if real_only:
        solutions = [
            solution
            for solution in solutions
            if all(
                is_real_solution(value)
                for value in solution.values()
            )
        ]

    return converted_solution_dict(
        solutions,
        variables,
    )


def builtin_simplify(context, value):
    if isinstance(value, SymbolicEquation):
        return from_sympy_equation(
            sp.simplify(value.left_expr),
            sp.simplify(value.right_expr),
        )

    return from_sympy_value(
        sp.simplify(
            to_sympy_expression(value)
        ),
        simplify=False,
    )


def builtin_expand(context, value):
    if isinstance(value, SymbolicEquation):
        return from_sympy_equation(
            sp.expand(value.left_expr),
            sp.expand(value.right_expr),
        )

    return from_sympy_value(
        sp.expand(
            to_sympy_expression(value)
        ),
        simplify=False,
    )


def builtin_develop(context, value):
    return builtin_expand(context, value)


def builtin_collect(context, value, variable):
    symbol = symbol_from_variable(variable)

    return from_sympy_value(
        sp.collect(
            to_sympy_expression(value),
            symbol,
        ),
        simplify=False,
    )


def builtin_factor(context, value):
    if is_symbolic(value):
        return from_sympy_value(
            sp.factor(
                to_sympy_expression(value)
            ),
            simplify=False,
        )

    return integer_prime_factors(value)


def builtin_subs(context, value, variable, replacement):
    expression = to_sympy_expression(value)
    replacements = substitution_pairs(
        variable,
        replacement,
    )

    result = expression.subs(replacements)

    if isinstance(value, SymbolicEquation):
        return SymbolicEquation(
            value.left_expr.subs(replacements),
            value.right_expr.subs(replacements),
        )

    return from_sympy_value(
        result,
        simplify=False,
    )


def builtin_coeffs(context, value, variable=None):
    expression = to_sympy_expression(value)

    if variable is None:
        symbols = sympy_symbols_for(value)
        variable = preferred_symbol(symbols)
    else:
        variable = symbol_from_variable(variable)

    try:
        polynomial = sp.Poly(
            expression,
            variable,
        )
    except sp.PolynomialError as error:
        raise Exception(
            f"coeffs: expression is not polynomial in {variable}"
        ) from error

    return np.array(
        [
            from_sympy_value(coefficient)
            for coefficient in polynomial.all_coeffs()
        ],
        dtype=object,
    )


def substitution_pairs(variable, replacement):
    variables = as_sequence(variable)
    replacements = as_sequence(replacement)

    if len(variables) != len(replacements):
        raise Exception(
            "subs requires the same number of variables and values"
        )

    return {
        symbol_from_variable(var): to_sympy_expression(value)
        for var, value in zip(variables, replacements)
    }


def integer_prime_factors(value):
    if isinstance(value, np.ndarray):
        if value.size != 1:
            raise Exception(
                "factor: numeric input must be a scalar integer"
            )

        value = value.item()

    if isinstance(value, np.generic):
        value = value.item()

    if isinstance(value, float):
        if not value.is_integer():
            raise Exception(
                "factor: numeric input must be an integer"
            )

        value = int(value)

    if not isinstance(value, int):
        raise Exception(
            "factor: numeric input must be an integer or symbolic expression"
        )

    if value < 2:
        raise Exception(
            "factor: numeric input must be >= 2"
        )

    factors = []
    remaining = value
    divisor = 2

    while divisor * divisor <= remaining:
        while remaining % divisor == 0:
            factors.append(divisor)
            remaining //= divisor

        divisor = 3 if divisor == 2 else divisor + 2

    if remaining > 1:
        factors.append(remaining)

    return np.array(factors)


def builtin_class(context, value):
    if is_symbolic(value):
        return "sym"

    if isinstance(value, (bool, np.bool_)):
        return "logical"

    if isinstance(value, np.ndarray):
        if np.issubdtype(value.dtype, np.bool_):
            return "logical"

        return "double"

    if isinstance(value, (int, float, complex, np.number, np.ndarray)):
        return "double"

    if isinstance(value, str):
        return "char"

    if isinstance(value, dict):
        return "struct"

    return type(value).__name__


def split_name_value_options(arguments):
    positional = []
    options = {}

    for argument in arguments:
        if isinstance(argument, NameValueOption):
            options[argument.name.lower()] = argument.value
        else:
            positional.append(argument)

    return positional, options


def preferred_symbol(symbols):
    if not symbols:
        raise Exception(
            "Unable to determine variable to solve for"
        )

    return sorted(
        symbols,
        key=symbol_sort_key,
    )[0]


def is_real_solution(value):
    real_state = sp.simplify(value).is_real

    return real_state is not False


def converted_solution_list(solutions):
    converted = [
        from_sympy_value(solution)
        for solution in solutions
    ]

    if len(converted) == 1:
        return converted[0]

    return np.array(
        converted,
        dtype=object,
    )


def converted_solution_dict(
    solutions,
    variables,
):
    if not solutions:
        return {
            variable.name: np.array(
                [],
                dtype=object,
            )
            for variable in variables
        }

    result = {}

    for variable in variables:
        values = [
            from_sympy_value(
                solution[variable]
            )
            for solution in solutions
            if variable in solution
        ]

        if len(values) == 1:
            result[variable.name] = values[0]
        else:
            result[variable.name] = np.array(
                values,
                dtype=object,
            )

    return result


BUILTIN_FUNCTIONS = {
    "disp": builtin_disp,
    "fprintf": builtin_fprintf,
    "warning": builtin_warning,
    "error": builtin_error,
    "help": builtin_help,
    "lookfor": builtin_lookfor,
    "cwd": builtin_cwd,
    "who": builtin_who,
    "struct": builtin_struct,

    "sin": builtin_sin,
    "cos": builtin_cos,
    "tan": builtin_tan,

    "asin": builtin_asin,
    "acos": builtin_acos,
    "atan": builtin_atan,
    "atan2": builtin_atan2,
    "sinh": builtin_sinh,
    "cosh": builtin_cosh,
    "tanh": builtin_tanh,
    "asinh": builtin_asinh,
    "acosh": builtin_acosh,
    "atanh": builtin_atanh,

    "log": builtin_log,
    "log10": builtin_log10,
    "log2": builtin_log2,
    "exp": builtin_exp,
    "expm1": builtin_expm1,

    "sqrt": builtin_sqrt,
    "angle": builtin_angle,
    "conj": builtin_conj,
    "imag": builtin_imag,
    "isreal": builtin_isreal,
    "real": builtin_real,
    "abs": builtin_abs,

    "floor": builtin_floor,
    "ceil": builtin_ceil,
    "round": builtin_round,
    "fix": builtin_fix,
    "clip": builtin_clip,
    "deg2rad": builtin_deg2rad,
    "rad2deg": builtin_rad2deg,
    "sign": builtin_sign,

    "zeros": builtin_zeros,
    "ones": builtin_ones,
    "true": builtin_true,
    "false": builtin_false,
    "zeros_like": builtin_zeros_like,
    "ones_like": builtin_ones_like,
    "linspace": builtin_linspace,
    "logspace": builtin_logspace,
    "arange": builtin_arange,
    "rand": builtin_rand,
    "randn": builtin_randn,
    "randi": builtin_randi,
    "rng": builtin_rng,
    "eye": builtin_eye,
    "reshape": builtin_reshape,
    "transpose": builtin_transpose,
    "flatten": builtin_flatten,
    "diag": builtin_diag,
    "tril": builtin_tril,
    "triu": builtin_triu,
    "det": builtin_det,
    "inv": builtin_inv,
    "pinv": builtin_pinv,
    "linsolve": builtin_linsolve,
    "eig": builtin_eig,
    "svd": builtin_svd,
    "qr": builtin_qr,
    "dot": builtin_dot,
    "cross": builtin_cross,
    "norm": builtin_norm,
    "trace": builtin_trace,
    "rank": builtin_rank,
    "cond": builtin_cond,
    "size": builtin_size,
    "numel": builtin_numel,
    "ndims": builtin_ndims,
    "isempty": builtin_isempty,
    "sum": builtin_sum,
    "prod": builtin_prod,
    "mean": builtin_mean,
    "median": builtin_median,
    "std": builtin_std,
    "var": builtin_var,
    "percentile": builtin_percentile,
    "max": builtin_max,
    "min": builtin_min,
    "any": builtin_any,
    "all": builtin_all,
    "isnan": builtin_isnan,
    "isinf": builtin_isinf,
    "isfinite": builtin_isfinite,
    "isclose": builtin_isclose,
    "allclose": builtin_allclose,
    "sort": builtin_sort,
    "unique": builtin_unique,
    "find": builtin_find,
    "diff": builtin_diff,
    "gradient": builtin_gradient,
    "cumsum": builtin_cumsum,
    "cumprod": builtin_cumprod,
    "trapz": builtin_trapz,
    "interp1": builtin_interp1,
    "fft": builtin_fft,
    "ifft": builtin_ifft,
    "fftshift": builtin_fftshift,
    "ifftshift": builtin_ifftshift,
    "fftfreq": builtin_fftfreq,
    "roots": builtin_roots,
    "polyval": builtin_polyval,
    "polyfit": builtin_polyfit,
    "conv": builtin_conv,
    "bode": builtin_bode,
    "nyquist": builtin_nyquist,

    "length": builtin_length,
    "plot": builtin_plot,
    "figure": builtin_figure,
    "close": builtin_close,
    "mod": builtin_mod,
    "title": builtin_title,
    "xlabel": builtin_xlabel,
    "ylabel": builtin_ylabel,
    "grid": builtin_grid,
    "sym": builtin_sym,
    "class": builtin_class,
    "complex": builtin_complex,
    "solve": builtin_solve,
    "symvar": builtin_symvar,
    "simplify": builtin_simplify,
    "collect": builtin_collect,
    "expand": builtin_expand,
    "develop": builtin_develop,
    "factor": builtin_factor,
    "subs": builtin_subs,
    "coeffs": builtin_coeffs,
}
