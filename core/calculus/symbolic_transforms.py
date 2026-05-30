import numpy as np
import sympy as sp

from core.errors.errors import RuntimeError as MathToolRuntimeError
from core.runtime.symbolic import (
    from_sympy_value,
    is_symbolic,
    symbol_from_variable,
    symbol_sort_key,
    sympy_symbols_for,
    to_sympy_expression,
)


DEFAULT_SYMBOLIC_PREFERENCES = {
    "FourierParameters": (sp.Integer(1), sp.Integer(-1)),
}


TRANSFORM_SPECS = {
    "laplace": {
        "default_var": "t",
        "default_trans_var": "s",
        "alternate_trans_var": "z",
        "fallback_var": "t",
    },
    "ilaplace": {
        "default_var": "s",
        "default_trans_var": "t",
        "alternate_trans_var": "x",
        "fallback_var": "s",
    },
    "fourier": {
        "default_var": None,
        "default_trans_var": "w",
        "alternate_trans_var": "v",
        "fallback_var": "x",
    },
    "ifourier": {
        "default_var": "w",
        "default_trans_var": "x",
        "alternate_trans_var": "t",
        "fallback_var": "w",
    },
    "ztrans": {
        "default_var": "n",
        "default_trans_var": "z",
        "alternate_trans_var": "w",
        "fallback_var": "n",
    },
    "iztrans": {
        "default_var": "z",
        "default_trans_var": "n",
        "alternate_trans_var": "k",
        "fallback_var": "z",
    },
}


def symbolic_laplace(expr, *arguments, preferences=None):
    return _symbolic_transform("laplace", expr, arguments, preferences)


def symbolic_ilaplace(expr, *arguments, preferences=None):
    return _symbolic_transform("ilaplace", expr, arguments, preferences)


def symbolic_fourier(expr, *arguments, preferences=None):
    return _symbolic_transform("fourier", expr, arguments, preferences)


def symbolic_ifourier(expr, *arguments, preferences=None):
    return _symbolic_transform("ifourier", expr, arguments, preferences)


def symbolic_ztrans(expr, *arguments, preferences=None):
    return _symbolic_transform("ztrans", expr, arguments, preferences)


def symbolic_iztrans(expr, *arguments, preferences=None):
    return _symbolic_transform("iztrans", expr, arguments, preferences)


def symbolic_dirac(value):
    return apply_symbolic_function_elementwise(
        lambda item: sp.DiracDelta(to_sympy_expression(item)),
        value,
    )


def symbolic_heaviside(value):
    return apply_symbolic_function_elementwise(
        lambda item: sp.Heaviside(to_sympy_expression(item)),
        value,
    )


def symbolic_kronecker_delta(left, right):
    arrays, shape = scalar_expand_transform_arguments(
        left,
        right,
        function_name="kroneckerDelta",
    )

    def evaluate(a, b):
        return from_sympy_value(
            sp.KroneckerDelta(
                to_sympy_expression(a),
                to_sympy_expression(b),
            ),
            simplify=False,
        )

    if shape is None:
        return evaluate(left, right)

    result = np.empty(shape, dtype=object)

    for index in np.ndindex(shape):
        result[index] = evaluate(arrays[0][index], arrays[1][index])

    return result


def symbolic_rectangular_pulse(*arguments):
    if len(arguments) == 1:
        left, right, value = (
            sp.Rational(-1, 2),
            sp.Rational(1, 2),
            arguments[0],
        )
    elif len(arguments) == 3:
        left, right, value = arguments
    else:
        raise MathToolRuntimeError(
            "rectangularPulse: expected 1 or 3 arguments"
        )

    return apply_symbolic_function_elementwise(
        lambda item: _rectangular_pulse_expr(left, right, item),
        value,
    )


def symbolic_triangular_pulse(*arguments):
    if len(arguments) == 1:
        left, center, right, value = (
            sp.Integer(-1),
            sp.Integer(0),
            sp.Integer(1),
            arguments[0],
        )
    elif len(arguments) == 4:
        left, center, right, value = arguments
    else:
        raise MathToolRuntimeError(
            "triangularPulse: expected 1 or 4 arguments"
        )

    return apply_symbolic_function_elementwise(
        lambda item: _triangular_pulse_expr(left, center, right, item),
        value,
    )


def apply_symbolic_function_elementwise(function, value):
    def evaluate(item):
        return from_sympy_value(function(item), simplify=False)

    if isinstance(value, np.ndarray):
        vectorized = np.vectorize(evaluate, otypes=[object])
        return vectorized(value)

    if isinstance(value, (list, tuple)):
        return np.array([evaluate(item) for item in value], dtype=object)

    return evaluate(value)


def default_symbolic_preferences():
    return dict(DEFAULT_SYMBOLIC_PREFERENCES)


def _symbolic_transform(transform_name, expr, arguments, preferences):
    var, trans_var = resolve_default_transform_variables(
        transform_name,
        expr,
        arguments,
    )

    return apply_transform_elementwise(
        expr,
        var,
        trans_var,
        lambda item, item_var, item_trans_var: _scalar_transform(
            transform_name,
            item,
            item_var,
            item_trans_var,
            preferences or DEFAULT_SYMBOLIC_PREFERENCES,
        ),
        transform_name,
    )


def resolve_default_transform_variables(transform_name, expr, arguments):
    if len(arguments) > 2:
        raise MathToolRuntimeError(
            f"{transform_name}: expected 1, 2, or 3 arguments"
        )

    if len(arguments) == 2:
        return arguments[0], arguments[1]

    spec = TRANSFORM_SPECS[transform_name]

    if len(arguments) == 1:
        return (
            resolve_default_variable(
                expr,
                spec["default_var"],
                spec["fallback_var"],
            ),
            arguments[0],
        )

    var = resolve_default_variable(
        expr,
        spec["default_var"],
        spec["fallback_var"],
    )

    trans_var = sp.Symbol(spec["default_trans_var"])

    if _symbol_name(var) == spec["default_trans_var"]:
        trans_var = sp.Symbol(spec["alternate_trans_var"])

    return var, trans_var


def resolve_default_variable(expr, preferred, fallback):
    expr_symbols = sympy_symbols_for(expr)
    symbols = sorted(expr_symbols, key=symbol_sort_key)

    if preferred is not None:
        for symbol in symbols:
            if symbol.name == preferred:
                return symbol

    if symbols:
        return symbols[0]

    return sp.Symbol(fallback or preferred)


def apply_transform_elementwise(expr, var, trans_var, transform_function, name):
    values, shape = scalar_expand_transform_arguments(
        expr,
        var,
        trans_var,
        function_name=name,
    )

    if shape is None:
        return transform_function(expr, var, trans_var)

    result = np.empty(shape, dtype=object)

    for index in np.ndindex(shape):
        result[index] = transform_function(
            values[0][index],
            values[1][index],
            values[2][index],
        )

    return result


def scalar_expand_transform_arguments(*arguments, function_name="transform"):
    arrays = []
    nonscalar_shapes = []

    for argument in arguments:
        if _is_nonscalar(argument):
            array = np.asarray(argument, dtype=object)
            arrays.append(array)
            nonscalar_shapes.append(array.shape)
        else:
            arrays.append(argument)

    if not nonscalar_shapes:
        return arrays, None

    shape = nonscalar_shapes[0]

    if any(item != shape for item in nonscalar_shapes):
        raise MathToolRuntimeError(
            f"{function_name}: nonscalar arguments must have compatible sizes"
        )

    expanded = []

    for value in arrays:
        if isinstance(value, np.ndarray) and value.shape == shape:
            expanded.append(value)
        else:
            filled = np.empty(shape, dtype=object)
            filled.fill(value)
            expanded.append(filled)

    return expanded, shape


def normalize_symbolic_transform_result(result, transform_name, expr, var, trans_var):
    if _is_unevaluated_transform_result(result):
        return make_unevaluated_transform(transform_name, expr, var, trans_var)

    return from_sympy_value(result, simplify=False)


def make_unevaluated_transform(transform_name, expr, var, trans_var):
    return from_sympy_value(
        sp.Function(transform_name)(
            to_sympy_expression(expr),
            to_sympy_expression(var),
            to_sympy_expression(trans_var),
        ),
        simplify=False,
    )


def _scalar_transform(transform_name, expr, var, trans_var, preferences):
    expression = to_sympy_expression(expr)
    variable = _symbolic_variable(var, transform_name, "independent variable")
    transform_variable = to_sympy_expression(trans_var)

    try:
        result = _compute_scalar_transform(
            transform_name,
            expression,
            variable,
            transform_variable,
            preferences,
        )
    except MathToolRuntimeError:
        raise
    except Exception:
        return make_unevaluated_transform(
            transform_name,
            expression,
            variable,
            transform_variable,
        )

    return normalize_symbolic_transform_result(
        result,
        transform_name,
        expression,
        variable,
        transform_variable,
    )


def _compute_scalar_transform(transform_name, expr, var, trans_var, preferences):
    temp_var, final_substitution = _transform_variable_target(trans_var)

    if transform_name == "laplace":
        result = sp.laplace_transform(expr, var, temp_var, noconds=True)
    elif transform_name == "ilaplace":
        result = sp.inverse_laplace_transform(expr, var, temp_var)
        result = result.subs(sp.Heaviside(temp_var), 1)
    elif transform_name == "fourier":
        result = _matlab_fourier(expr, var, temp_var, preferences)
    elif transform_name == "ifourier":
        result = _matlab_ifourier(expr, var, temp_var, preferences)
    elif transform_name == "ztrans":
        result = _z_transform(expr, var, temp_var)
    elif transform_name == "iztrans":
        result = _inverse_z_transform(expr, var, temp_var)
    else:
        raise MathToolRuntimeError(
            f"{transform_name}: unsupported symbolic transform"
        )

    if final_substitution is not None:
        result = result.subs(temp_var, final_substitution)

    return result


def _matlab_fourier(expr, var, trans_var, preferences):
    c, s = _fourier_parameters(preferences)

    if not expr.has(var):
        return 2 * sp.pi * c * expr * sp.DiracDelta(trans_var)

    return c * sp.fourier_transform(
        expr,
        var,
        -s * trans_var / (2 * sp.pi),
    )


def _matlab_ifourier(expr, var, trans_var, preferences):
    c, s = _fourier_parameters(preferences)

    if not expr.has(var):
        return expr * sp.DiracDelta(trans_var) / c

    helper = sp.Dummy("fourier_k")
    transformed_expr = expr.subs(
        var,
        2 * sp.pi * helper / (-s),
    )
    result = sp.inverse_fourier_transform(
        transformed_expr,
        helper,
        trans_var,
    )
    return result / (c * (-s))


def _fourier_parameters(preferences):
    params = preferences.get(
        "FourierParameters",
        DEFAULT_SYMBOLIC_PREFERENCES["FourierParameters"],
    )
    return (
        to_sympy_expression(params[0]),
        to_sympy_expression(params[1]),
    )


def _z_transform(expr, var, trans_var):
    result = sp.summation(
        expr * trans_var ** (-var),
        (var, 0, sp.oo),
    )

    return _strip_convergence_piecewise(sp.simplify(result))


def _inverse_z_transform(expr, var, trans_var):
    rational_result = _inverse_z_transform_by_residue(expr, var, trans_var)

    if rational_result is not None:
        return rational_result

    series_result = _inverse_z_transform_by_series(expr, var, trans_var)

    if series_result is not None:
        return series_result

    return make_unevaluated_transform("iztrans", expr, var, trans_var).sympy_expr


def _inverse_z_transform_by_residue(expr, var, trans_var):
    try:
        expression = sp.together(expr)
        denominator = sp.denom(expression)
        poles = [
            pole
            for pole in sp.solve(sp.Eq(denominator, 0), var)
            if pole != 0
        ]
    except Exception:
        return None

    if not poles:
        return None

    terms = []
    kernel = expression * var ** (trans_var - 1)

    for pole in poles:
        try:
            terms.append(sp.residue(kernel, var, pole))
        except Exception:
            return None

    return sp.simplify(sum(terms))


def _inverse_z_transform_by_series(expr, var, trans_var):
    if not isinstance(trans_var, sp.Symbol):
        return None

    helper = sp.Dummy("z_series")

    try:
        generating = to_sympy_expression(expr).subs(var, 1 / helper)
    except Exception:
        return None

    if generating == helper:
        return sp.KroneckerDelta(trans_var, 1)

    if generating == 1:
        return sp.KroneckerDelta(trans_var, 0)

    return None


def _strip_convergence_piecewise(result):
    if isinstance(result, sp.Piecewise) and result.args:
        return result.args[0].expr

    return result


def _transform_variable_target(trans_var):
    if isinstance(trans_var, sp.Symbol):
        return trans_var, None

    return sp.Dummy("transform_var"), trans_var


def _symbolic_variable(value, transform_name, label):
    try:
        return symbol_from_variable(value)
    except Exception as error:
        raise MathToolRuntimeError(
            f"{transform_name}: {label} must be symbolic"
        ) from error


def _is_unevaluated_transform_result(result):
    unevaluated_types = (
        sp.LaplaceTransform,
        sp.InverseLaplaceTransform,
        sp.FourierTransform,
        sp.InverseFourierTransform,
        sp.Integral,
        sp.Sum,
    )

    return isinstance(result, unevaluated_types) or result.has(*unevaluated_types)


def _rectangular_pulse_expr(left, right, value):
    left_expr = to_sympy_expression(left)
    right_expr = to_sympy_expression(right)
    value_expr = to_sympy_expression(value)

    return sp.Piecewise(
        (sp.Integer(1), (value_expr >= left_expr) & (value_expr <= right_expr)),
        (sp.Integer(0), True),
    )


def _triangular_pulse_expr(left, center, right, value):
    left_expr = to_sympy_expression(left)
    center_expr = to_sympy_expression(center)
    right_expr = to_sympy_expression(right)
    value_expr = to_sympy_expression(value)

    rising = (value_expr - left_expr) / (center_expr - left_expr)
    falling = (right_expr - value_expr) / (right_expr - center_expr)

    return sp.Piecewise(
        (rising, (value_expr >= left_expr) & (value_expr <= center_expr)),
        (falling, (value_expr > center_expr) & (value_expr <= right_expr)),
        (sp.Integer(0), True),
    )


def _is_nonscalar(value):
    if isinstance(value, np.ndarray):
        return value.ndim > 0 and value.size > 1

    return isinstance(value, (list, tuple)) and len(value) > 1


def _symbol_name(value):
    try:
        expression = to_sympy_expression(value)
    except Exception:
        return None

    if isinstance(expression, sp.Symbol):
        return expression.name

    return None
