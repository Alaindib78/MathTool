import math
import numpy as np
import sympy as sp

from core.control import (
    FrequencyResponseModel,
    StateSpaceModel,
    TransferFunctionModel,
    ZeroPoleGainModel,
    acker as control_acker,
    append as control_append,
    bandwidth as control_bandwidth,
    bode_magnitude,
    bode_response,
    c2d as control_c2d,
    care as control_care,
    controllability_matrix,
    d2c as control_d2c,
    damping as control_damping,
    dare as control_dare,
    dc_gain,
    dlqr as control_dlqr,
    dlyap as control_dlyap,
    feedback as control_feedback,
    frequency_response,
    gramian,
    initial_response,
    impulse_response,
    is_continuous_time,
    is_discrete_time,
    is_lti_model,
    is_stable,
    lqr as control_lqr,
    lsim_response,
    lyap as control_lyap,
    minreal as control_minreal,
    nyquist_response,
    observability_matrix,
    parallel as control_parallel,
    pid as control_pid,
    place as control_place,
    poles as control_poles,
    root_locus_data,
    series as control_series,
    stability_margins,
    step_info,
    step_response,
    to_state_space,
    to_transfer_function,
    to_zero_pole_gain,
    zeros as control_zeros,
)
from core.calculus import (
    FunctionHandle,
    numerical_gradient,
    numerical_integral,
    numerical_integral2,
    symbolic_dirac,
    symbolic_diff,
    symbolic_fourier,
    symbolic_heaviside,
    symbolic_ifourier,
    symbolic_ilaplace,
    symbolic_integral,
    symbolic_iztrans,
    symbolic_kronecker_delta,
    symbolic_laplace,
    symbolic_limit,
    symbolic_rectangular_pulse,
    symbolic_triangular_pulse,
    symbolic_ztrans,
    trapezoidal_integral,
)
from core.errors.errors import RuntimeError as MathToolRuntimeError
from core.numerics import (
    fzero_solver,
    newton_solver,
    secant_solver,
)
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
from core.runtime.user_input import request_user_input
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
        display_format=context.display_format,
    )

    return None


def builtin_print(context, *args):
    if not args:
        disp(
            "",
            output_callback=context.output_callback,
            display_format=context.display_format,
        )
        return None

    for value in args:
        disp(
            value,
            output_callback=context.output_callback,
            display_format=context.display_format,
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


def builtin_input(context, prompt, mode=None):
    return request_user_input(
        context,
        prompt,
        mode,
    )


def builtin_format(context, *styles):
    try:
        context.display_format.apply(*styles)
    except ValueError as error:
        raise MathToolRuntimeError(str(error)) from error

    return None


def builtin_formatsettings(context):
    settings = context.display_format.settings

    return {
        "NumericFormat": settings.numeric_format,
        "LineSpacing": settings.spacing_mode,
    }


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
    return _unary_math(x, np.sin, sp.sin)


def builtin_cos(context,x):
    return _unary_math(x, np.cos, sp.cos)


def builtin_tan(context,x):
    return _unary_math(x, np.tan, sp.tan)

def builtin_asin(context,x):
    return _unary_math(x, np.arcsin, sp.asin)


def builtin_acos(context,x):
    return _unary_math(x, np.arccos, sp.acos)


def builtin_atan(context,x):
    return _unary_math(x, np.arctan, sp.atan)


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
    return _unary_math(x, np.log, sp.log)

def builtin_log10(context,x):
    return _unary_math(
        x,
        np.log10,
        lambda expression: sp.log(expression, 10),
    )


def builtin_log2(context, x):
    return np.log2(x)


def builtin_exp(context,x):
    return _unary_math(x, np.exp, sp.exp)


def builtin_expm1(context, x):
    return np.expm1(x)


def builtin_sqrt(context,x):
    if is_symbolic(x):
        return _unary_math(x, np.sqrt, sp.sqrt)

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
    return _unary_math(x, np.abs, sp.Abs)

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
    return _unary_math(x, np.sign, sp.sign)


def _unary_math(value, numeric_function, symbolic_function):
    if is_symbolic(value):
        def apply(item):
            return from_sympy_value(
                symbolic_function(
                    to_sympy_expression(item)
                )
            )

        if isinstance(value, np.ndarray):
            return np.vectorize(
                apply,
                otypes=[object],
            )(value)

        if isinstance(value, (list, tuple)):
            return np.array(
                [apply(item) for item in value],
                dtype=object,
            )

        return apply(value)

    return numeric_function(value)

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
    return (
        np.flatnonzero(
            _as_array(value).reshape(-1, order="F")
        )
        + 1
    )


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


def builtin_diff(context, value, *arguments):
    if is_symbolic(value):
        return symbolic_diff(value, *arguments)

    n = 1
    dim = None

    if len(arguments) > 2:
        raise MathToolRuntimeError(
            "diff: expected diff(A), diff(A,n), "
            "or diff(A,n,dim)"
        )

    if len(arguments) >= 1:
        n = arguments[0]

    if len(arguments) == 2:
        dim = arguments[1]

    array = _as_array(value)
    axis = (
        _first_nonsingleton_axis(array)
        if dim is None
        else _axis_from_dim(dim)
    )

    return np.diff(array, n=int(n), axis=axis)


def builtin_gradient(context, value, *spacing):
    return numerical_gradient(value, *spacing)


def builtin_cumsum(context, value, dim=None):
    array = _as_array(value)
    axis = None if dim is None else _axis_from_dim(dim)

    return _normalize_result(np.cumsum(array, axis=axis))


def builtin_cumprod(context, value, dim=None):
    array = _as_array(value)
    axis = None if dim is None else _axis_from_dim(dim)

    return _normalize_result(np.cumprod(array, axis=axis))


def builtin_trapz(context, *arguments):
    return trapezoidal_integral(*arguments)


def builtin_int(context, value, *arguments):
    return symbolic_integral(value, *arguments)


def builtin_limit(context, value, *arguments):
    return symbolic_limit(value, *arguments)


def builtin_laplace(context, value, *arguments):
    return symbolic_laplace(
        value,
        *arguments,
        preferences=context.symbolic_preferences,
    )


def builtin_ilaplace(context, value, *arguments):
    return symbolic_ilaplace(
        value,
        *arguments,
        preferences=context.symbolic_preferences,
    )


def builtin_fourier(context, value, *arguments):
    return symbolic_fourier(
        value,
        *arguments,
        preferences=context.symbolic_preferences,
    )


def builtin_ifourier(context, value, *arguments):
    return symbolic_ifourier(
        value,
        *arguments,
        preferences=context.symbolic_preferences,
    )


def builtin_ztrans(context, value, *arguments):
    return symbolic_ztrans(
        value,
        *arguments,
        preferences=context.symbolic_preferences,
    )


def builtin_iztrans(context, value, *arguments):
    return symbolic_iztrans(
        value,
        *arguments,
        preferences=context.symbolic_preferences,
    )


def builtin_integral(context, fun, xmin, xmax, *arguments):
    return numerical_integral(
        fun,
        xmin,
        xmax,
        *arguments,
    )


def builtin_integral2(
    context,
    fun,
    xmin,
    xmax,
    ymin,
    ymax,
    *arguments,
):
    return numerical_integral2(
        fun,
        xmin,
        xmax,
        ymin,
        ymax,
        *arguments,
    )


def builtin_interp1(context, x, y, query):
    return _normalize_result(
        np.interp(
            query,
            _as_array(x),
            _as_array(y),
        )
    )


def builtin_fzero(context, fun, x0=None, *arguments):
    if x0 is None:
        raise MathToolRuntimeError(
            "fzero expects fzero(fun, x0)"
        )

    return fzero_solver(
        fun,
        x0,
        *arguments,
        output_callback=context.output_callback,
    )


def builtin_newtons_method(context, fun, derivative, x0=None, *arguments):
    if x0 is None:
        raise MathToolRuntimeError(
            "newtons_method expects newtons_method(f, df, x0)"
        )

    return newton_solver(
        fun,
        derivative,
        x0,
        *arguments,
        output_callback=context.output_callback,
    )


def builtin_secant(context, fun, x0=None, x1=None, *arguments):
    if x0 is None or x1 is None:
        raise MathToolRuntimeError(
            "secant expects secant(f, x0, x1)"
        )

    return secant_solver(
        fun,
        x0,
        x1,
        *arguments,
        output_callback=context.output_callback,
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


def _split_lti_options(arguments):
    positional = []
    options = {}
    option_names = {
        "inputdelay",
        "outputdelay",
    "iodelay",
    "io_delay",
    "name",
    "inputunit",
    "outputunit",
    }
    index = 0

    while index < len(arguments):
        argument = arguments[index]

        if isinstance(argument, NameValueOption):
            options[argument.name.lower()] = argument.value
            index += 1
            continue

        if (
            isinstance(argument, str)
            and argument.lower() in option_names
        ):
            if index + 1 >= len(arguments):
                raise MathToolRuntimeError(
                    f"lti: option '{argument}' requires a value"
                )

            options[argument.lower()] = arguments[index + 1]
            index += 2
            continue

        positional.append(argument)
        index += 1

    normalized = {}
    for name, value in options.items():
        key = name.lower()

        if key == "inputdelay":
            normalized["input_delay"] = value
        elif key == "outputdelay":
            normalized["output_delay"] = value
        elif key in {"iodelay", "io_delay"}:
            normalized["io_delay"] = value
        elif key == "name":
            normalized["name"] = str(value)
        elif key == "inputunit":
            normalized["input_unit"] = value
        elif key == "outputunit":
            normalized["output_unit"] = value
        else:
            raise MathToolRuntimeError(
                f"lti: unsupported option '{name}'"
            )

    return positional, normalized


def builtin_tf(context, *arguments):
    positional, options = _split_lti_options(arguments)

    if len(positional) == 1 and is_lti_model(positional[0]):
        if options:
            raise MathToolRuntimeError(
                "tf: options are not supported when converting an LTI model"
            )
        return to_transfer_function(positional[0])

    if len(positional) in {1, 2} and isinstance(positional[0], str):
        variable = positional[0].lower()
        Ts = positional[1] if len(positional) == 2 else 0.0

        if options:
            raise MathToolRuntimeError(
                "tf: options are not supported for transfer variables"
            )

        return TransferFunctionModel.variable(variable, Ts)

    if len(positional) not in {2, 3}:
        raise MathToolRuntimeError(
            "tf: expected tf(num, den), tf(num, den, Ts), tf(sys), or tf('s')"
        )

    Ts = positional[2] if len(positional) == 3 else 0.0
    return TransferFunctionModel(
        positional[0],
        positional[1],
        Ts,
        **options,
    )


def builtin_ss(context, *arguments):
    positional, options = _split_lti_options(arguments)

    if len(positional) == 1 and is_lti_model(positional[0]):
        if options:
            raise MathToolRuntimeError(
                "ss: options are not supported when converting an LTI model"
            )
        return to_state_space(positional[0])

    if len(positional) not in {4, 5}:
        raise MathToolRuntimeError(
            "ss: expected ss(A, B, C, D), ss(A, B, C, D, Ts), or ss(sys)"
        )

    Ts = positional[4] if len(positional) == 5 else 0.0
    return StateSpaceModel(
        positional[0],
        positional[1],
        positional[2],
        positional[3],
        Ts,
        **options,
    )


def builtin_zpk(context, *arguments):
    positional, options = _split_lti_options(arguments)

    if len(positional) == 1 and is_lti_model(positional[0]):
        if options:
            raise MathToolRuntimeError(
                "zpk: options are not supported when converting an LTI model"
            )
        return to_zero_pole_gain(positional[0])

    if len(positional) not in {3, 4}:
        raise MathToolRuntimeError(
            "zpk: expected zpk(z, p, k), zpk(z, p, k, Ts), or zpk(sys)"
        )

    Ts = positional[3] if len(positional) == 4 else 0.0
    return ZeroPoleGainModel(
        positional[0],
        positional[1],
        positional[2],
        Ts,
        **options,
    )


def builtin_frd(context, *arguments):
    positional, options = _split_lti_options(arguments)

    if len(positional) not in {2, 3}:
        raise MathToolRuntimeError(
            "frd: expected frd(response, frequencies) or frd(response, frequencies, Ts)"
        )

    Ts = positional[2] if len(positional) == 3 else 0.0
    return FrequencyResponseModel(
        positional[0],
        positional[1],
        Ts,
        **options,
    )


def builtin_get(context, value):
    if is_lti_model(value):
        return value.properties()

    if hasattr(value, "properties") and callable(value.properties):
        return value.properties()

    if isinstance(value, dict):
        return value

    raise MathToolRuntimeError(
        f"get: expected object with properties, LTI model, or struct, got {type(value).__name__}"
    )


def builtin_pole(context, model):
    return control_poles(model)


def builtin_zero(context, model):
    return control_zeros(model)


def builtin_minreal(context, model, tolerance=1e-6):
    return control_minreal(model, float(tolerance))


def builtin_damp(context, model):
    return control_damping(model)


def builtin_dcgain(context, model):
    return dc_gain(model)


def builtin_isstable(context, model):
    return is_stable(model)


def _warn_if_delayed(context, function_name, model):
    if is_lti_model(model) and model.has_delay():
        warning(
            "%s: model delays are stored but ignored by this analysis",
            function_name,
            output_callback=context.output_callback,
        )


def _plot_time_response(context, t, y, title_text, y_label):
    context.plot_engine.figure()
    context.plot_engine.plot(t, y)
    context.plot_engine.title(title_text)
    context.plot_engine.xlabel("Time (seconds)")
    context.plot_engine.ylabel(y_label)
    context.plot_engine.grid_on()


def builtin_step(context, model, time=None):
    _warn_if_delayed(context, "step", model)
    t, y = step_response(model, time)
    _plot_time_response(
        context,
        t,
        y,
        "Step Response",
        "Amplitude",
    )
    return None


def builtin_impulse(context, model, time=None):
    _warn_if_delayed(context, "impulse", model)
    t, y = impulse_response(model, time)
    _plot_time_response(
        context,
        t,
        y,
        "Impulse Response",
        "Amplitude",
    )
    return None


def builtin_initial(context, model, x0, time=None):
    _warn_if_delayed(context, "initial", model)
    t, y = initial_response(model, x0, time)
    _plot_time_response(
        context,
        t,
        y,
        "Initial Condition Response",
        "Amplitude",
    )
    return None


def builtin_lsim(context, model, u, time):
    _warn_if_delayed(context, "lsim", model)
    t, y = lsim_response(model, u, time)
    _plot_time_response(
        context,
        t,
        y,
        "Simulated Response",
        "Amplitude",
    )
    return None


def builtin_stepinfo(context, model, time=None):
    return step_info(model, time)


def builtin_freqresp(context, model, frequency):
    return frequency_response(model, frequency)


def builtin_bandwidth(context, model):
    return control_bandwidth(model)


def builtin_bodemag(context, model, frequency=None):
    w, magnitude_db = bode_magnitude(model, frequency)
    context.plot_engine.figure()
    context.plot_engine.plot(w, magnitude_db)
    context.plot_engine.title("Bode Magnitude")
    context.plot_engine.xlabel("Frequency (rad/s)")
    context.plot_engine.ylabel("Magnitude (dB)")
    context.plot_engine.grid_on()
    return None


def builtin_nichols(context, model, frequency=None):
    w, magnitude_db, phase_deg = bode_response(model, frequency)
    context.plot_engine.figure()
    context.plot_engine.plot(phase_deg, magnitude_db)
    context.plot_engine.title("Nichols Chart")
    context.plot_engine.xlabel("Phase (deg)")
    context.plot_engine.ylabel("Magnitude (dB)")
    context.plot_engine.grid_on()
    return None


def builtin_sigma(context, model, frequency=None):
    w, magnitude_db = bode_magnitude(model, frequency)
    context.plot_engine.figure()
    context.plot_engine.plot(w, magnitude_db)
    context.plot_engine.title("Singular Values")
    context.plot_engine.xlabel("Frequency (rad/s)")
    context.plot_engine.ylabel("Magnitude (dB)")
    context.plot_engine.grid_on()
    return None


def builtin_margin(context, model, frequency=None):
    margins = stability_margins(model, frequency)

    if context.output_callback is not None:
        context.output_callback(
            "Stability margins:\n"
            f"    GainMargin: {margins['GainMargin']}\n"
            f"    PhaseMargin: {margins['PhaseMargin']}\n"
            f"    GMFrequency: {margins['GMFrequency']}\n"
            f"    PMFrequency: {margins['PMFrequency']}\n\n"
        )

    builtin_bode(context, model, frequency) if frequency is not None else builtin_bode(context, model)
    return margins


def builtin_allmargin(context, model, frequency=None):
    margins = stability_margins(model, frequency)
    margins["Stable"] = is_stable(model)
    return margins


def builtin_rlocus(context, model, gains=None):
    roots, gain_values = root_locus_data(model, gains)
    context.plot_engine.figure()
    previous_hold = getattr(context.plot_engine, "hold_enabled", False)
    if hasattr(context.plot_engine, "hold"):
        context.plot_engine.hold("on")

    try:
        if roots.ndim == 2:
            for column in range(roots.shape[1]):
                branch = roots[:, column]
                context.plot_engine.plot(np.real(branch), np.imag(branch))

        open_loop_poles = control_poles(model)
        open_loop_zeros = control_zeros(model)

        if len(open_loop_poles):
            context.plot_engine.plot(
                np.real(open_loop_poles),
                np.imag(open_loop_poles),
                "x",
            )

        if len(open_loop_zeros):
            context.plot_engine.plot(
                np.real(open_loop_zeros),
                np.imag(open_loop_zeros),
                "o",
            )
    finally:
        if hasattr(context.plot_engine, "hold"):
            context.plot_engine.hold(previous_hold)

    context.plot_engine.title("Root Locus")
    context.plot_engine.xlabel("Real Axis")
    context.plot_engine.ylabel("Imaginary Axis")
    context.plot_engine.grid_on()
    return {
        "roots": roots,
        "gains": gain_values,
    }


def builtin_series(context, sys1, sys2):
    return control_series(sys1, sys2)


def builtin_parallel(context, sys1, sys2):
    return control_parallel(sys1, sys2)


def builtin_feedback(context, sys1, sys2=1, sign=-1):
    return control_feedback(sys1, sys2, sign)


def builtin_append(context, *systems):
    return control_append(*systems)


def builtin_ctrb(context, A_or_sys, B=None):
    return controllability_matrix(A_or_sys, B)


def builtin_obsv(context, A_or_sys, C=None):
    return observability_matrix(A_or_sys, C)


def builtin_gram(context, sys, kind):
    return gramian(sys, kind)


def builtin_lyap(context, A, Q):
    return control_lyap(A, Q)


def builtin_dlyap(context, A, Q):
    return control_dlyap(A, Q)


def builtin_care(context, A, B, Q, R):
    return control_care(A, B, Q, R)


def builtin_dare(context, A, B, Q, R):
    return control_dare(A, B, Q, R)


def builtin_place(context, A, B, desired_poles):
    return control_place(A, B, desired_poles)


def builtin_acker(context, A, B, desired_poles):
    return control_acker(A, B, desired_poles)


def builtin_lqr(context, A, B, Q, R):
    return control_lqr(A, B, Q, R)


def builtin_dlqr(context, A, B, Q, R):
    return control_dlqr(A, B, Q, R)


def builtin_pid(context, Kp, Ki=0.0, Kd=0.0):
    return control_pid(Kp, Ki, Kd)


def builtin_pidtune(context, model, controller_type="PID"):
    gain = dc_gain(model)
    if isinstance(gain, np.ndarray):
        gain = np.asarray(gain).reshape(-1)[0]

    gain = float(np.real(gain))
    base = 1.0 if np.isclose(gain, 0) else 1.0 / abs(gain)
    kind = str(controller_type).lower()

    if kind == "p":
        return control_pid(base, 0, 0)

    if kind == "pi":
        return control_pid(base, 0.5 * base, 0)

    if kind == "pid":
        return control_pid(base, 0.5 * base, 0.1 * base)

    raise MathToolRuntimeError(
        "pidtune: controller type must be 'P', 'PI', or 'PID'"
    )


def builtin_c2d(context, model, Ts, method="zoh"):
    return control_c2d(model, Ts, method)


def builtin_d2c(context, model, method="zoh"):
    return control_d2c(model, method)


def builtin_isdt(context, model):
    return is_discrete_time(model)


def builtin_isct(context, model):
    return is_continuous_time(model)


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


def builtin_bode(context, *arguments):
    if arguments and is_lti_model(arguments[0]):
        if len(arguments) > 2:
            raise MathToolRuntimeError(
                "bode: expected bode(sys) or bode(sys, w)"
            )

        model = arguments[0]
        frequency = arguments[1] if len(arguments) == 2 else None
        _warn_if_delayed(context, "bode", model)
        frequency, magnitude_db, phase_deg = bode_response(
            model,
            frequency,
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

    if len(arguments) not in {2, 3}:
        raise MathToolRuntimeError(
            "bode: expected bode(sys), bode(sys, w), bode(num, den), or bode(num, den, w)"
        )

    numerator = arguments[0]
    denominator = arguments[1]
    frequency = arguments[2] if len(arguments) == 3 else None

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


def builtin_nyquist(context, *arguments):
    if arguments and is_lti_model(arguments[0]):
        if len(arguments) > 2:
            raise MathToolRuntimeError(
                "nyquist: expected nyquist(sys) or nyquist(sys, w)"
            )

        model = arguments[0]
        frequency = arguments[1] if len(arguments) == 2 else None
        real_values, imag_values = nyquist_response(model, frequency)

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

    if len(arguments) not in {2, 3}:
        raise MathToolRuntimeError(
            "nyquist: expected nyquist(sys), nyquist(sys, w), nyquist(num, den), or nyquist(num, den, w)"
        )

    numerator = arguments[0]
    denominator = arguments[1]
    frequency = arguments[2] if len(arguments) == 3 else None

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

def builtin_plot(context, *arguments):
    return context.plot_engine.plot(*arguments)

def builtin_histogram(context, *arguments):
    return context.plot_engine.histogram(*arguments)

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


def _as_integer(value, function_name):
    if isinstance(value, np.generic):
        value = value.item()

    if isinstance(value, bool):
        raise Exception(
            f"{function_name}: input must be an integer"
        )

    if isinstance(value, float):
        if not value.is_integer():
            raise Exception(
                f"{function_name}: input must be an integer"
            )

        value = int(value)

    if not isinstance(value, (int, np.integer)):
        raise Exception(
            f"{function_name}: input must be an integer"
        )

    return int(value)


def _map_array_or_scalar(value, converter):
    if isinstance(value, np.ndarray):
        if value.ndim == 0:
            return converter(value.item())

        return [
            converter(item)
            for item in value.reshape(-1, order="C")
        ]

    if isinstance(value, (list, tuple)):
        return [
            converter(item)
            for item in np.asarray(value).reshape(-1, order="C")
        ]

    return converter(value)


def builtin_dec2hex(context, value):
    def convert(item):
        integer = _as_integer(item, "dec2hex")

        if integer < 0:
            raise Exception(
                "dec2hex: input must be a nonnegative integer"
            )

        return format(integer, "X")

    return _map_array_or_scalar(value, convert)


def builtin_dec2bin(context, value):
    def convert(item):
        integer = _as_integer(item, "dec2bin")

        if integer < 0:
            raise Exception(
                "dec2bin: input must be a nonnegative integer"
            )

        return format(integer, "b")

    return _map_array_or_scalar(value, convert)


def _as_text(value, function_name):
    if isinstance(value, np.generic):
        value = value.item()

    if not isinstance(value, str):
        raise Exception(
            f"{function_name}: input must be a string"
        )

    return value.strip()


def builtin_hex2dec(context, value):
    def convert(item):
        text = _as_text(item, "hex2dec")

        if text.lower().startswith("0x"):
            text = text[2:]

        if (
            not text
            or any(char not in "0123456789abcdefABCDEF" for char in text)
        ):
            raise Exception(
                "hex2dec: input must contain hexadecimal digits"
            )

        return int(text, 16)

    return _map_array_or_scalar(value, convert)


def builtin_bin2dec(context, value):
    def convert(item):
        text = _as_text(item, "bin2dec")

        if text.lower().startswith("0b"):
            text = text[2:]

        if not text or any(char not in "01" for char in text):
            raise Exception(
                "bin2dec: input must contain binary digits"
            )

        return int(text, 2)

    return _map_array_or_scalar(value, convert)


def builtin_bitand(context, a, b):
    return _normalize_result(np.bitwise_and(a, b))


def builtin_bitor(context, a, b):
    return _normalize_result(np.bitwise_or(a, b))


def builtin_bitxor(context, a, b):
    return _normalize_result(np.bitwise_xor(a, b))


def builtin_bitshift(context, a, k):
    shift = _as_integer(k, "bitshift")

    if shift >= 0:
        return _normalize_result(np.left_shift(a, shift))

    return _normalize_result(np.right_shift(a, abs(shift)))


def builtin_bitget(context, a, bit):
    bit_index = _as_integer(bit, "bitget")

    if bit_index < 1:
        raise Exception(
            "bitget: bit position must be positive"
        )

    return _normalize_result(
        np.bitwise_and(
            np.right_shift(a, bit_index - 1),
            1,
        )
    )


def builtin_bitset(context, a, bit, value=True):
    bit_index = _as_integer(bit, "bitset")

    if bit_index < 1:
        raise Exception(
            "bitset: bit position must be positive"
        )

    mask = 1 << (bit_index - 1)

    if bool(value):
        return _normalize_result(np.bitwise_or(a, mask))

    array = np.asarray(a)

    if np.issubdtype(array.dtype, np.integer):
        clear_mask = np.bitwise_not(
            np.asarray(mask, dtype=array.dtype)
        )

        return _normalize_result(np.bitwise_and(a, clear_mask))

    return _normalize_result(np.bitwise_and(a, ~mask))


def builtin_title(context, text):
    context.plot_engine.title(text)


def builtin_xlabel(context, text):
    context.plot_engine.xlabel(text)


def builtin_ylabel(context, text):
    context.plot_engine.ylabel(text)


def builtin_grid(context, value=True):
    if isinstance(value, str):
        lowered = value.lower()

        if lowered == "on":
            value = True
        elif lowered == "off":
            value = False

    if value:
        context.plot_engine.grid_on()
    else:
        context.plot_engine.grid_off()


def builtin_hold(context, value=None):
    if hasattr(context.plot_engine, "hold"):
        return context.plot_engine.hold(value)

    return None


def builtin_xticks(context, *arguments):
    return context.plot_engine.xticks(*arguments)


def builtin_xticklabels(context, *arguments):
    return context.plot_engine.xticklabels(*arguments)


def builtin_yticks(context, *arguments):
    return context.plot_engine.yticks(*arguments)


def builtin_yticklabels(context, *arguments):
    return context.plot_engine.yticklabels(*arguments)


def builtin_xline(context, *arguments):
    return context.plot_engine.xline(*arguments)


def builtin_yline(context, *arguments):
    return context.plot_engine.yline(*arguments)


def builtin_legend(context, *arguments):
    return context.plot_engine.legend(*arguments)


def builtin_subplot(context, *arguments):
    return context.plot_engine.subplot(*arguments)


def builtin_axis(context, *arguments):
    return context.plot_engine.axis(*arguments)


def builtin_sym(context, value):
    if isinstance(value, SymbolicValue):
        return value

    return SymbolicValue(value)


def builtin_syms(context, *names):
    if not names:
        raise MathToolRuntimeError(
            "syms: expected at least one variable name"
        )

    created = []

    for name in names:
        if not isinstance(name, str):
            raise MathToolRuntimeError(
                "syms: variable names must be strings"
            )

        value = SymbolicValue(name)
        context.set_variable(name, value)
        created.append(value)

    if len(created) == 1:
        return created[0]

    return np.array(created, dtype=object)


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


def builtin_dirac(context, value):
    return symbolic_dirac(value)


def builtin_heaviside(context, value):
    return symbolic_heaviside(value)


def builtin_kroneckerdelta(context, left, right):
    return symbolic_kronecker_delta(left, right)


def builtin_rectangularpulse(context, *arguments):
    return symbolic_rectangular_pulse(*arguments)


def builtin_triangularpulse(context, *arguments):
    return symbolic_triangular_pulse(*arguments)


def builtin_sympref(context, name=None, value=None):
    if name is None:
        return {
            key: np.array(values, dtype=object)
            if isinstance(values, tuple)
            else values
            for key, values in context.symbolic_preferences.items()
        }

    normalized = str(name).strip().lower()

    if normalized == "default":
        context.symbolic_preferences.clear()
        context.symbolic_preferences.update(
            {
                "FourierParameters": (
                    sp.Integer(1),
                    sp.Integer(-1),
                )
            }
        )
        return None

    if normalized != "fourierparameters":
        raise MathToolRuntimeError(
            f"sympref: unsupported preference '{name}'"
        )

    if value is None:
        return np.array(
            context.symbolic_preferences["FourierParameters"],
            dtype=object,
        )

    if isinstance(value, str):
        if value.strip().lower() != "default":
            raise MathToolRuntimeError(
                'sympref: FourierParameters must be a two-element vector or "default"'
            )

        context.symbolic_preferences["FourierParameters"] = (
            sp.Integer(1),
            sp.Integer(-1),
        )
        return None

    values = as_sequence(value)

    if len(values) != 2:
        raise MathToolRuntimeError(
            'sympref: FourierParameters must be a two-element vector or "default"'
        )

    context.symbolic_preferences["FourierParameters"] = (
        to_sympy_expression(values[0]),
        to_sympy_expression(values[1]),
    )

    return None


def builtin_pretty(context, value):
    text = sp.pretty(to_sympy_expression(value))

    if context.output_callback is not None:
        context.output_callback(text + "\n")
        return None

    return text


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
    if isinstance(value, FunctionHandle):
        return "function_handle"

    if is_lti_model(value):
        return value.model_type

    if is_symbolic(value):
        return "sym"

    if isinstance(value, (bool, np.bool_)):
        return "logical"

    if isinstance(value, np.ndarray):
        if np.issubdtype(value.dtype, np.bool_):
            return "logical"

        if np.issubdtype(value.dtype, np.unsignedinteger):
            return f"uint{value.dtype.itemsize * 8}"

        if np.issubdtype(value.dtype, np.signedinteger):
            return f"int{value.dtype.itemsize * 8}"

        return "double"

    if isinstance(value, np.unsignedinteger):
        return f"uint{value.dtype.itemsize * 8}"

    if isinstance(value, np.signedinteger):
        return f"int{value.dtype.itemsize * 8}"

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
    "print": builtin_print,
    "fprintf": builtin_fprintf,
    "warning": builtin_warning,
    "error": builtin_error,
    "input": builtin_input,
    "format": builtin_format,
    "formatsettings": builtin_formatsettings,
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
    "int": builtin_int,
    "limit": builtin_limit,
    "laplace": builtin_laplace,
    "ilaplace": builtin_ilaplace,
    "fourier": builtin_fourier,
    "ifourier": builtin_ifourier,
    "ztrans": builtin_ztrans,
    "iztrans": builtin_iztrans,
    "integral": builtin_integral,
    "integral2": builtin_integral2,
    "fzero": builtin_fzero,
    "newtons_method": builtin_newtons_method,
    "newton": builtin_newtons_method,
    "newton_raphson": builtin_newtons_method,
    "secant": builtin_secant,
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
    "tf": builtin_tf,
    "ss": builtin_ss,
    "zpk": builtin_zpk,
    "frd": builtin_frd,
    "get": builtin_get,
    "minreal": builtin_minreal,
    "pole": builtin_pole,
    "zero": builtin_zero,
    "damp": builtin_damp,
    "dcgain": builtin_dcgain,
    "isstable": builtin_isstable,
    "step": builtin_step,
    "impulse": builtin_impulse,
    "initial": builtin_initial,
    "lsim": builtin_lsim,
    "stepinfo": builtin_stepinfo,
    "bode": builtin_bode,
    "bodemag": builtin_bodemag,
    "nyquist": builtin_nyquist,
    "nichols": builtin_nichols,
    "sigma": builtin_sigma,
    "freqresp": builtin_freqresp,
    "bandwidth": builtin_bandwidth,
    "margin": builtin_margin,
    "allmargin": builtin_allmargin,
    "rlocus": builtin_rlocus,
    "series": builtin_series,
    "parallel": builtin_parallel,
    "feedback": builtin_feedback,
    "append": builtin_append,
    "ctrb": builtin_ctrb,
    "obsv": builtin_obsv,
    "gram": builtin_gram,
    "lyap": builtin_lyap,
    "dlyap": builtin_dlyap,
    "care": builtin_care,
    "dare": builtin_dare,
    "place": builtin_place,
    "acker": builtin_acker,
    "lqr": builtin_lqr,
    "dlqr": builtin_dlqr,
    "pid": builtin_pid,
    "pidtune": builtin_pidtune,
    "c2d": builtin_c2d,
    "d2c": builtin_d2c,
    "isdt": builtin_isdt,
    "isct": builtin_isct,

    "length": builtin_length,
    "plot": builtin_plot,
    "histogram": builtin_histogram,
    "figure": builtin_figure,
    "close": builtin_close,
    "mod": builtin_mod,
    "dec2hex": builtin_dec2hex,
    "dec2bin": builtin_dec2bin,
    "hex2dec": builtin_hex2dec,
    "bin2dec": builtin_bin2dec,
    "bitand": builtin_bitand,
    "bitor": builtin_bitor,
    "bitxor": builtin_bitxor,
    "bitshift": builtin_bitshift,
    "bitget": builtin_bitget,
    "bitset": builtin_bitset,
    "title": builtin_title,
    "xlabel": builtin_xlabel,
    "ylabel": builtin_ylabel,
    "grid": builtin_grid,
    "hold": builtin_hold,
    "xticks": builtin_xticks,
    "xticklabels": builtin_xticklabels,
    "yticks": builtin_yticks,
    "yticklabels": builtin_yticklabels,
    "xline": builtin_xline,
    "yline": builtin_yline,
    "legend": builtin_legend,
    "subplot": builtin_subplot,
    "axis": builtin_axis,
    "sym": builtin_sym,
    "syms": builtin_syms,
    "class": builtin_class,
    "complex": builtin_complex,
    "solve": builtin_solve,
    "symvar": builtin_symvar,
    "dirac": builtin_dirac,
    "heaviside": builtin_heaviside,
    "kroneckerDelta": builtin_kroneckerdelta,
    "rectangularPulse": builtin_rectangularpulse,
    "triangularPulse": builtin_triangularpulse,
    "sympref": builtin_sympref,
    "pretty": builtin_pretty,
    "simplify": builtin_simplify,
    "collect": builtin_collect,
    "expand": builtin_expand,
    "develop": builtin_develop,
    "factor": builtin_factor,
    "subs": builtin_subs,
    "coeffs": builtin_coeffs,
}
