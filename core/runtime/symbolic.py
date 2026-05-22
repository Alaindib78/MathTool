import re

import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    parse_expr,
    standard_transformations,
)


SYMPY_TRANSFORMATIONS = (
    standard_transformations
    + (convert_xor,)
)


class SymbolicValue:
    __array_priority__ = 1000

    def __init__(self, expression):
        self.sympy_expr = to_sympy_expression(expression)

    @property
    def expression(self):
        return sympy_text(self.sympy_expr)

    def __str__(self):
        return self.expression

    def __repr__(self):
        return self.expression

    def __eq__(self, other):
        if not is_symbolic(other):
            return False

        return symbolic_equal(
            self.sympy_expr,
            to_sympy_expression(other),
        )

    def __neg__(self):
        return SymbolicValue(-self.sympy_expr)

    def __pos__(self):
        return self

    def __add__(self, other):
        return symbolic_binary_value(self, other, "add")

    def __radd__(self, other):
        return symbolic_binary_value(other, self, "add")

    def __sub__(self, other):
        return symbolic_binary_value(self, other, "sub")

    def __rsub__(self, other):
        return symbolic_binary_value(other, self, "sub")

    def __mul__(self, other):
        return symbolic_binary_value(self, other, "mul")

    def __rmul__(self, other):
        return symbolic_binary_value(other, self, "mul")

    def __truediv__(self, other):
        return symbolic_binary_value(self, other, "div")

    def __rtruediv__(self, other):
        return symbolic_binary_value(other, self, "div")

    def __pow__(self, other):
        return symbolic_binary_value(self, other, "pow")

    def __rpow__(self, other):
        return symbolic_binary_value(other, self, "pow")


class SymbolicEquation:
    def __init__(self, left, right):
        self.left_expr = to_sympy_expression(left)
        self.right_expr = to_sympy_expression(right)

    @property
    def left(self):
        return sympy_text(self.left_expr)

    @property
    def right(self):
        return sympy_text(self.right_expr)

    @property
    def expression(self):
        return f"{self.left} == {self.right}"

    def __str__(self):
        return self.expression

    def __repr__(self):
        return self.expression

    def __eq__(self, other):
        if not isinstance(other, SymbolicEquation):
            return False

        return (
            symbolic_equal(self.left_expr, other.left_expr)
            and symbolic_equal(self.right_expr, other.right_expr)
        )


class NameValueOption:
    def __init__(self, name, value):
        self.name = str(name)
        self.value = value


def is_symbolic(value):
    if isinstance(value, (SymbolicValue, SymbolicEquation, sp.Basic)):
        return True

    if isinstance(value, np.ndarray):
        return any(
            is_symbolic(item)
            for item in value.flat
        )

    return False


def to_sympy_expression(value):
    if isinstance(value, SymbolicValue):
        return value.sympy_expr

    if isinstance(value, SymbolicEquation):
        return value.left_expr - value.right_expr

    if isinstance(value, sp.Basic):
        return value

    if isinstance(value, np.generic):
        value = value.item()

    if isinstance(value, bool):
        return sp.sympify(value)

    if isinstance(value, int):
        return sp.Integer(value)

    if isinstance(value, float):
        if value.is_integer():
            return sp.Integer(int(value))

        return sp.Float(value)

    if isinstance(value, complex):
        return (
            to_sympy_expression(value.real)
            + sp.I * to_sympy_expression(value.imag)
        )

    if isinstance(value, str):
        return parse_symbolic_text(value)

    return sp.sympify(value)


def to_sympy_equation(value):
    if isinstance(value, SymbolicEquation):
        return sp.Eq(
            value.left_expr,
            value.right_expr,
        )

    expression = to_sympy_expression(value)

    return sp.Eq(expression, 0)


def parse_symbolic_text(text):
    normalized = normalize_symbolic_text(text)

    return parse_expr(
        normalized,
        transformations=SYMPY_TRANSFORMATIONS,
        evaluate=True,
    )


def normalize_symbolic_text(text):
    text = str(text).strip()
    text = text.replace("^", "**")

    # SymPy parses I as the imaginary unit, while MathTool accepts 1i/1j.
    text = re.sub(
        r"(?<=\d)([ij])\b",
        r"*I",
        text,
    )

    return text


def sympy_text(value):
    if isinstance(value, SymbolicValue):
        return value.expression

    if isinstance(value, SymbolicEquation):
        return value.expression

    expression = to_sympy_expression(value)
    text = sp.sstr(expression)
    text = text.replace("**", "^")
    text = text.replace("I", "1i")

    return text


def from_sympy_value(value, *, simplify=True):
    expression = to_sympy_expression(value)

    if simplify:
        expression = sp.simplify(expression)

    return SymbolicValue(expression)


def from_sympy_equation(left, right, *, simplify=False):
    left_expr = to_sympy_expression(left)
    right_expr = to_sympy_expression(right)

    if simplify:
        left_expr = sp.simplify(left_expr)
        right_expr = sp.simplify(right_expr)

    return SymbolicEquation(left_expr, right_expr)


def symbolic_binary_value(left, right, operation):
    left_expr = to_sympy_expression(left)
    right_expr = to_sympy_expression(right)

    if operation == "add":
        result = left_expr + right_expr
    elif operation == "sub":
        result = left_expr - right_expr
    elif operation == "mul":
        result = left_expr * right_expr
    elif operation == "div":
        result = left_expr / right_expr
    elif operation == "pow":
        result = left_expr ** right_expr
    else:
        raise ValueError(f"Unsupported symbolic operation '{operation}'")

    return SymbolicValue(result)


def symbolic_equal(left, right):
    difference = sp.simplify(
        to_sympy_expression(left)
        - to_sympy_expression(right)
    )

    return difference == 0


def sympy_symbols_for(value):
    symbols = set()

    for item in as_sequence(value):
        if isinstance(item, SymbolicEquation):
            symbols.update(item.left_expr.free_symbols)
            symbols.update(item.right_expr.free_symbols)
        else:
            symbols.update(
                to_sympy_expression(item).free_symbols
            )

    return sorted(
        symbols,
        key=symbol_sort_key,
    )


def as_sequence(value):
    if isinstance(value, np.ndarray):
        return list(value.flatten())

    if isinstance(value, (list, tuple)):
        return list(value)

    return [value]


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


def symbol_from_variable(value):
    expression = to_sympy_expression(value)

    if isinstance(expression, sp.Symbol):
        return expression

    raise Exception(
        "symbolic variable arguments must be symbolic variables"
    )
