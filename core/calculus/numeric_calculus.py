import numpy as np

from core.calculus.function_handle import FunctionHandle
from core.errors.errors import RuntimeError as MathToolRuntimeError


def numerical_integral(fun, xmin, xmax, *arguments):
    integrate = _require_scipy_integrate("integral")
    _require_callable(fun, "integral")

    options = _parse_options(
        "integral",
        arguments,
        {
            "abstol",
            "reltol",
            "arrayvalued",
            "vectorized",
            "waypoints",
        },
    )

    lower = _numeric_scalar(xmin, "integral: xmin")
    upper = _numeric_scalar(xmax, "integral: xmax")
    epsabs = _positive_tolerance(
        options.get("abstol", 1.49e-8),
        "integral: AbsTol",
        allow_zero=True,
    )
    epsrel = _positive_tolerance(
        options.get("reltol", 1.49e-8),
        "integral: RelTol",
        allow_zero=True,
    )
    array_valued = bool(options.get("arrayvalued", False))

    if array_valued:
        if not hasattr(integrate, "quad_vec"):
            raise MathToolRuntimeError(
                "integral: ArrayValued requires scipy.integrate.quad_vec"
            )

        result, _ = integrate.quad_vec(
            lambda x: np.asarray(fun(x)),
            lower,
            upper,
            epsabs=epsabs,
            epsrel=epsrel,
        )
        return _normalize_result(result)

    points = options.get("waypoints")
    if points is not None:
        points = np.asarray(points, dtype=float).reshape(-1)

    result, _ = integrate.quad(
        lambda x: float(np.asarray(fun(x))),
        lower,
        upper,
        epsabs=epsabs,
        epsrel=epsrel,
        points=points,
    )
    return _normalize_result(result)


def numerical_integral2(
    fun,
    xmin,
    xmax,
    ymin,
    ymax,
    *arguments,
):
    integrate = _require_scipy_integrate("integral2")
    _require_callable(fun, "integral2")

    options = _parse_options(
        "integral2",
        arguments,
        {
            "abstol",
            "reltol",
            "method",
            "vectorized",
        },
    )

    method = str(options.get("method", "auto")).lower()
    if method not in {"auto", "iterated", "tiled"}:
        raise MathToolRuntimeError(
            f"integral2: invalid Method '{method}'"
        )

    lower_x = _numeric_scalar(xmin, "integral2: xmin")
    upper_x = _numeric_scalar(xmax, "integral2: xmax")
    epsabs = _positive_tolerance(
        options.get("abstol", 1.49e-8),
        "integral2: AbsTol",
        allow_zero=True,
    )
    epsrel = _positive_tolerance(
        options.get("reltol", 1.49e-8),
        "integral2: RelTol",
        allow_zero=True,
    )

    def y_lower(x):
        return _bound_value(ymin, x, "integral2: ymin")

    def y_upper(x):
        return _bound_value(ymax, x, "integral2: ymax")

    result, _ = integrate.dblquad(
        lambda y, x: float(np.asarray(fun(x, y))),
        lower_x,
        upper_x,
        y_lower,
        y_upper,
        epsabs=epsabs,
        epsrel=epsrel,
    )

    return _normalize_result(result)


def trapezoidal_integral(*arguments):
    if not arguments:
        raise MathToolRuntimeError(
            "trapz: expected at least one argument"
        )

    if len(arguments) > 3:
        raise MathToolRuntimeError(
            "trapz: expected trapz(Y), trapz(X,Y), "
            "trapz(Y,dim), or trapz(X,Y,dim)"
        )

    if len(arguments) == 1:
        y = np.asarray(arguments[0])
        axis = _first_nonsingleton_axis(y)
        return _trapz(y, axis=axis)

    if len(arguments) == 2:
        first = arguments[0]
        second = arguments[1]

        if _is_dimension_argument(second):
            y = np.asarray(first)
            return _trapz(
                y,
                axis=_axis_from_dim(second, y.ndim),
            )

        x = np.asarray(first)
        y = np.asarray(second)
        axis = _first_nonsingleton_axis(y)
        return _trapz_with_x(x, y, axis)

    x = np.asarray(arguments[0])
    y = np.asarray(arguments[1])
    axis = _axis_from_dim(arguments[2], y.ndim)
    return _trapz_with_x(x, y, axis)


def numerical_gradient(value, *spacing):
    array = np.asarray(value, dtype=float)

    try:
        result = np.gradient(array, *spacing)
    except Exception as error:
        raise MathToolRuntimeError(
            f"gradient: {error}"
        ) from error

    if isinstance(result, (list, tuple)):
        if array.ndim == 2 and len(result) >= 2:
            return (result[1], result[0])

        return tuple(result)

    return _normalize_result(result)


def _trapz_with_x(x, y, axis):
    if x.ndim == 0:
        return _normalize_result(
            float(x) * _trapz(y, axis=axis)
        )

    if x.ndim == 1 and y.ndim > 0 and x.size != y.shape[axis]:
        raise MathToolRuntimeError(
            "trapz: X length must match integration dimension"
        )

    return _trapz(y, x=x, axis=axis)


def _trapz(y, x=None, axis=-1):
    func = getattr(np, "trapezoid", None)
    if func is None:
        func = np.trapz

    return _normalize_result(func(y, x=x, axis=axis))


def _parse_options(function_name, arguments, allowed):
    options = {}
    index = 0

    while index < len(arguments):
        argument = arguments[index]

        if hasattr(argument, "name") and hasattr(argument, "value"):
            key = str(argument.name).lower()
            if key not in allowed:
                raise MathToolRuntimeError(
                    f"{function_name}: unknown option '{argument.name}'"
                )
            options[key] = argument.value
            index += 1
            continue

        if not isinstance(argument, str):
            raise MathToolRuntimeError(
                f"{function_name}: expected Name,Value options"
            )

        if index + 1 >= len(arguments):
            raise MathToolRuntimeError(
                f"{function_name}: missing value for option '{argument}'"
            )

        key = argument.lower()
        if key not in allowed:
            raise MathToolRuntimeError(
                f"{function_name}: unknown option '{argument}'"
            )

        options[key] = arguments[index + 1]
        index += 2

    return options


def _require_callable(value, function_name):
    if not isinstance(value, FunctionHandle) and not callable(value):
        raise MathToolRuntimeError(
            f"{function_name}: first argument must be a function handle"
        )


def _require_scipy_integrate(function_name):
    try:
        from scipy import integrate
    except ImportError as error:
        raise MathToolRuntimeError(
            f"{function_name}: scipy is required"
        ) from error

    return integrate


def _bound_value(bound, x, label):
    if isinstance(bound, FunctionHandle) or callable(bound):
        return _numeric_scalar(bound(x), label)

    return _numeric_scalar(bound, label)


def _numeric_scalar(value, label):
    array = np.asarray(value, dtype=float)

    if array.ndim != 0:
        raise MathToolRuntimeError(
            f"{label} must be numeric scalar"
        )

    return float(array)


def _positive_tolerance(value, label, *, allow_zero=False):
    tolerance = _numeric_scalar(value, label)

    if allow_zero:
        valid = tolerance >= 0
    else:
        valid = tolerance > 0

    if not valid:
        raise MathToolRuntimeError(
            f"{label} must be positive"
        )

    return tolerance


def _axis_from_dim(dim, ndim):
    axis = int(dim) - 1

    if axis < 0:
        raise MathToolRuntimeError(
            "trapz: dim must be positive"
        )

    if ndim > 0 and axis >= ndim:
        raise MathToolRuntimeError(
            "trapz: dim exceeds array dimensions"
        )

    return axis


def _is_dimension_argument(value):
    if isinstance(value, bool):
        return False

    if isinstance(value, (int, np.integer)):
        return True

    if isinstance(value, float):
        return value.is_integer()

    return False


def _first_nonsingleton_axis(array):
    for axis, size in enumerate(array.shape):
        if size > 1:
            return axis

    return 0


def _normalize_result(value):
    if isinstance(value, np.generic):
        return value.item()

    array = np.asarray(value)

    if array.ndim == 0:
        return array.item()

    return value
