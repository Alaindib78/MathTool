import numpy as np
import sympy as sp

from core.errors.errors import RuntimeError as MathToolRuntimeError
from core.runtime.symbolic import (
    SymbolicEquation,
    from_sympy_equation,
    from_sympy_value,
    is_symbolic,
    symbol_from_variable,
    symbol_sort_key,
    sympy_symbols_for,
    to_sympy_equation,
    to_sympy_expression,
)


def symbolic_diff(value, *arguments):
    if not is_symbolic(value):
        raise MathToolRuntimeError(
            "diff: expected symbolic expression"
        )

    def differentiate(item):
        expr = to_sympy_expression(item)
        spec = _diff_spec(expr, arguments)
        result = sp.diff(expr, *spec)
        return from_sympy_value(result)

    return _map_symbolic(value, differentiate)


def symbolic_integral(value, *arguments):
    positional, options = _split_symbolic_options(arguments)
    hold = bool(options.get("hold", False))

    unsupported = set(options) - {
        "hold",
        "ignoreanalyticconstraints",
        "ignorespecialcases",
        "principalvalue",
    }

    if unsupported:
        name = sorted(unsupported)[0]
        raise MathToolRuntimeError(
            f"int: unsupported option '{name}'"
        )

    if any(
        bool(options.get(name, False))
        for name in (
            "ignoreanalyticconstraints",
            "ignorespecialcases",
            "principalvalue",
        )
    ):
        # SymPy does not expose MATLAB's exact switches here. These
        # options are accepted as best-effort compatibility flags.
        pass

    def integrate(item):
        expr = to_sympy_expression(item)
        spec = _integral_spec(expr, positional)
        if hold:
            result = sp.Integral(expr, *spec)
        else:
            result = sp.integrate(expr, *spec)

        return from_sympy_value(result, simplify=not hold)

    if isinstance(value, SymbolicEquation):
        equation = to_sympy_equation(value)
        left = integrate(equation.lhs)
        right = integrate(equation.rhs)
        return from_sympy_equation(
            to_sympy_expression(left),
            to_sympy_expression(right),
        )

    return _map_symbolic(value, integrate)


def symbolic_limit(value, *arguments):
    var, point, direction = _limit_spec(value, arguments)

    return apply_limit_elementwise(value, var, point, direction)


def apply_limit_elementwise(value, var=None, point=0, direction=None):
    if _is_multivariable_limit_request(var, point):
        raise MathToolRuntimeError(
            "limit: multivariable limits are not supported yet; "
            "use iterated limits explicitly"
        )

    normalized_direction = normalize_limit_direction(direction)
    converted_point = convert_limit_point(point)

    def limit_item(item):
        if not is_symbolic(item):
            return item

        expr = to_sympy_expression(item)
        symbol = var

        if symbol is None:
            symbol = resolve_default_symbol(expr)

        if symbol is None:
            return item

        result = _sympy_limit(expr, symbol, converted_point, normalized_direction)
        return matlab_limit_result(result)

    if isinstance(value, SymbolicEquation):
        equation = to_sympy_equation(value)
        left = limit_item(equation.lhs)
        right = limit_item(equation.rhs)
        return from_sympy_equation(
            to_sympy_expression(left),
            to_sympy_expression(right),
        )

    return _map_symbolic(value, limit_item)


def resolve_default_symbol(expr):
    symbols = sorted(
        sympy_symbols_for(expr),
        key=symbol_sort_key,
    )

    if not symbols:
        return None

    for symbol in symbols:
        if symbol.name == "x":
            return symbol

    return symbols[0]


def convert_limit_point(value):
    return to_sympy_expression(value)


def normalize_limit_direction(direction):
    if direction is None:
        return None

    if not isinstance(direction, str):
        raise MathToolRuntimeError(
            'limit: direction must be "left" or "right"'
        )

    normalized = direction.strip().lower()

    if normalized in {"left", "l", "-"}:
        return "left"

    if normalized in {"right", "r", "+"}:
        return "right"

    raise MathToolRuntimeError(
        'limit: direction must be "left" or "right"'
    )


def matlab_limit_result(sympy_result):
    return from_sympy_value(sympy_result, simplify=False)


def _sympy_limit(expr, var, point, direction):
    if direction == "left":
        return sp.limit(expr, var, point, dir="-")

    if direction == "right":
        return sp.limit(expr, var, point, dir="+")

    left_error = None
    right_error = None

    try:
        left = sp.limit(expr, var, point, dir="-")
    except Exception as error:
        left_error = error
        left = None

    try:
        right = sp.limit(expr, var, point, dir="+")
    except Exception as error:
        right_error = error
        right = None

    if left_error is None and right_error is None:
        if _limits_equal(left, right):
            return left

        return sp.nan

    try:
        return sp.limit(expr, var, point)
    except Exception:
        if left_error is not None:
            raise MathToolRuntimeError(
                f"limit: unable to compute limit ({left_error})"
            ) from left_error

        raise MathToolRuntimeError(
            f"limit: unable to compute limit ({right_error})"
        ) from right_error


def _limits_equal(left, right):
    if left == right:
        return True

    try:
        return sp.simplify(left - right) == 0
    except Exception:
        return False


def _limit_spec(value, arguments):
    if len(arguments) == 0:
        return None, 0, None

    if len(arguments) == 1:
        return None, arguments[0], None

    if len(arguments) == 2:
        return _limit_variable(arguments[0]), arguments[1], None

    if len(arguments) == 3:
        return (
            _limit_variable(arguments[0]),
            arguments[1],
            normalize_limit_direction(arguments[2]),
        )

    raise MathToolRuntimeError(
        "limit: invalid number of arguments"
    )


def _limit_variable(value):
    if _is_multivariable_argument(value):
        return value

    try:
        return symbol_from_variable(value)
    except Exception as error:
        raise MathToolRuntimeError(
            "limit: variable argument must be symbolic variable"
        ) from error


def _is_multivariable_limit_request(var, point):
    return _is_multivariable_argument(var) or _is_multivariable_argument(point)


def _is_multivariable_argument(value):
    if value is None:
        return False

    if isinstance(value, np.ndarray):
        return value.ndim > 0 and value.size > 1

    return isinstance(value, (list, tuple)) and len(value) > 1


def _map_symbolic(value, operation):
    if isinstance(value, np.ndarray):
        vectorized = np.vectorize(
            operation,
            otypes=[object],
        )
        return vectorized(value)

    if (
        isinstance(value, (list, tuple))
        and any(is_symbolic(item) for item in value)
    ):
        return np.array(
            [operation(item) for item in value],
            dtype=object,
        )

    return operation(value)


def _diff_spec(expr, arguments):
    if not arguments:
        return (_default_diff_symbol(expr),)

    if len(arguments) == 1 and _is_nonnegative_integer(arguments[0]):
        return (
            _default_diff_symbol(expr),
            int(arguments[0]),
        )

    spec = []
    index = 0
    while index < len(arguments):
        variable = symbol_from_variable(arguments[index])

        if (
            index + 1 < len(arguments)
            and _is_nonnegative_integer(arguments[index + 1])
        ):
            spec.extend(
                [variable, int(arguments[index + 1])]
            )
            index += 2
        else:
            spec.append(variable)
            index += 1

    return tuple(spec)


def _integral_spec(expr, arguments):
    if not arguments:
        return (_default_integral_symbol(expr),)

    if len(arguments) == 1:
        return (symbol_from_variable(arguments[0]),)

    if len(arguments) == 2:
        variable = _default_integral_symbol(expr)
        lower = to_sympy_expression(arguments[0])
        upper = to_sympy_expression(arguments[1])
        return ((variable, lower, upper),)

    if len(arguments) == 3:
        variable = symbol_from_variable(arguments[0])
        lower = to_sympy_expression(arguments[1])
        upper = to_sympy_expression(arguments[2])
        return ((variable, lower, upper),)

    raise MathToolRuntimeError(
        "int: expected int(expr), int(expr,var), "
        "int(expr,a,b), or int(expr,var,a,b)"
    )


def _default_diff_symbol(expr):
    symbols = sorted(
        sympy_symbols_for(expr),
        key=symbol_sort_key,
    )

    if symbols:
        return symbols[0]

    return sp.Symbol("x")


def _default_integral_symbol(expr):
    return _default_diff_symbol(expr)


def _is_nonnegative_integer(value):
    if isinstance(value, bool):
        return False

    if isinstance(value, (int, np.integer)):
        return int(value) >= 0

    if isinstance(value, float):
        return value.is_integer() and value >= 0

    return False


def _split_symbolic_options(arguments):
    positional = []
    options = {}
    index = 0

    while index < len(arguments):
        argument = arguments[index]
        name = None

        if hasattr(argument, "name") and hasattr(argument, "value"):
            name = str(argument.name).lower()
            options[name] = argument.value
            index += 1
            continue

        if (
            isinstance(argument, str)
            and index + 1 < len(arguments)
            and _looks_like_option_name(argument)
        ):
            name = argument.lower()
            options[name] = arguments[index + 1]
            index += 2
            continue

        positional.append(argument)
        index += 1

    return positional, options


def _looks_like_option_name(value):
    return value.lower() in {
        "hold",
        "ignoreanalyticconstraints",
        "ignorespecialcases",
        "principalvalue",
    }
