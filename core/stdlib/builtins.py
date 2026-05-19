import math
from pydoc import text
import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    parse_expr,
    standard_transformations,
)

from core.runtime.formatting import format_value
from core.runtime.symbolic import (
    NameValueOption,
    SymbolicEquation,
    SymbolicValue,
)
from core.stdlib.console import (
    disp,
    error as console_error,
    fprintf,
    warning,
)


SYMPY_TRANSFORMATIONS = (
    standard_transformations
    + (convert_xor,)
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

def builtin_log(context,x):
    return np.log(x)

def builtin_log10(context,x):
    return np.log10(x)


def builtin_exp(context,x):
    return np.exp(x)


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

def builtin_round(context,x):
    return np.round(x)

def builtin_sign(context,x):
    return np.sign(x)   

def builtin_zeros(context, rows, cols=None):
    rows = int(rows)

    if cols is None:
        cols = rows
    else:
        cols = int(cols)

    return np.zeros((rows, cols))


def builtin_ones(context, rows, cols=None):
    rows = int(rows)

    if cols is None:
        cols = rows
    else:
        cols = int(cols)

    return np.ones((rows, cols))


def _as_array(value):
    return np.asarray(value)


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
        axis = int(dim) - 1

        if axis < 0:
            raise Exception("Dimension must be positive")

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
        return np.sum(array)

    return np.sum(array, axis=int(dim) - 1)


def builtin_mean(context, value, dim=None):
    array = _as_array(value)

    if dim is None:
        return np.mean(array)

    return np.mean(array, axis=int(dim) - 1)


def builtin_max(context, value, dim=None):
    array = _as_array(value)

    if dim is None:
        return np.max(array)

    return np.max(array, axis=int(dim) - 1)


def builtin_min(context, value, dim=None):
    array = _as_array(value)

    if dim is None:
        return np.min(array)

    return np.min(array, axis=int(dim) - 1)


def builtin_length(context,x):
    return len(x)

def builtin_plot(context, x, y):
    context.plot_engine.plot(x, y)

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


def builtin_class(context, value):
    if isinstance(
        value,
        (
            SymbolicValue,
            SymbolicEquation,
        )
    ):
        return "sym"

    if isinstance(value, bool):
        return "logical"

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


def as_sequence(value):
    if isinstance(value, np.ndarray):
        return list(value.flatten())

    if isinstance(value, (list, tuple)):
        return list(value)

    return [value]


def to_sympy_equation(value):
    if isinstance(value, SymbolicEquation):
        return sp.Eq(
            to_sympy_expression(value.left),
            to_sympy_expression(value.right),
        )

    expression = to_sympy_expression(value)

    return sp.Eq(expression, 0)


def to_sympy_expression(value):
    if isinstance(value, SymbolicValue):
        value = value.expression

    if isinstance(value, SymbolicEquation):
        value = value.expression

    if isinstance(value, bool):
        return sp.sympify(value)

    if isinstance(value, (int, float, complex, np.number)):
        return sp.sympify(value)

    text_value = str(value)

    return parse_expr(
        text_value.replace("^", "**"),
        transformations=SYMPY_TRANSFORMATIONS,
        evaluate=True,
    )


def sympy_symbols_for(value):
    symbols = set()

    for item in as_sequence(value):
        if isinstance(item, SymbolicEquation):
            symbols.update(
                to_sympy_expression(item.left).free_symbols
            )
            symbols.update(
                to_sympy_expression(item.right).free_symbols
            )
        else:
            symbols.update(
                to_sympy_expression(item).free_symbols
            )

    return sorted(
        symbols,
        key=symbol_sort_key,
    )


def symbol_sort_key(symbol):
    preferred_names = [
        "x",
        "y",
        "z",
        "t",
    ]

    if symbol.name in preferred_names:
        return (
            0,
            preferred_names.index(symbol.name),
        )

    return (
        1,
        symbol.name,
    )


def preferred_symbol(symbols):
    if not symbols:
        raise Exception(
            "Unable to determine variable to solve for"
        )

    return sorted(
        symbols,
        key=symbol_sort_key,
    )[0]


def symbol_from_variable(value):
    if isinstance(value, SymbolicValue):
        return sp.Symbol(value.expression)

    if isinstance(value, str):
        return sp.Symbol(value)

    raise Exception(
        "solve variables must be symbolic variables"
    )


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


def from_sympy_value(value):
    value = sp.simplify(value)

    return SymbolicValue(
        sympy_text(value)
    )


def sympy_text(value):
    text_value = sp.sstr(value)
    text_value = text_value.replace("**", "^")
    text_value = text_value.replace("I", "1i")

    return text_value


BUILTIN_FUNCTIONS = {
    "disp": builtin_disp,
    "fprintf": builtin_fprintf,
    "warning": builtin_warning,
    "error": builtin_error,

    "sin": builtin_sin,
    "cos": builtin_cos,
    "tan": builtin_tan,

    "asin": builtin_sin,
    "acos": builtin_acos,
    "atan": builtin_atan,

    "log": builtin_log,
    "log10": builtin_log10,
    "exp": builtin_exp,

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
    "sign": builtin_sign,

    "zeros": builtin_zeros,
    "ones": builtin_ones,
    "eye": builtin_eye,
    "det": builtin_det,
    "inv": builtin_inv,
    "size": builtin_size,
    "sum": builtin_sum,
    "mean": builtin_mean,
    "max": builtin_max,
    "min": builtin_min,

    "length": builtin_length,
    "plot": builtin_plot,
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
}
