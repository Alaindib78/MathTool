import numpy as np
import pytest

from core.errors.errors import RuntimeError as MathToolRuntimeError
from core.runtime.context import RuntimeContext
from core.runtime.symbolic import SymbolicValue


def test_interpreter_evaluates_arithmetic_and_assignments(execute):
    result, context = execute(
        """
A = 2 + 3 * 4;
B = A / 2;
B;
"""
    )

    assert result == 7
    assert context.variables["A"] == 14
    assert context.variables["B"] == 7


def test_interpreter_applies_scalar_arithmetic_to_range_vectors(execute):
    _, context = execute(
        """
t = 0:0.1:0.2;
twice_left = 2 * t;
twice_right = t * 2;
shifted = t + 1;
reflected = 1 - t;
halved = t / 2;
powers = t ^ 2;
mask = t >= 0.2;
negative = -(1:3);
y = sin(2 * t);
"""
    )

    np.testing.assert_allclose(
        context.variables["twice_left"],
        np.array([0, 0.2, 0.4]),
    )
    np.testing.assert_allclose(
        context.variables["twice_right"],
        np.array([0, 0.2, 0.4]),
    )
    np.testing.assert_allclose(
        context.variables["shifted"],
        np.array([1, 1.1, 1.2]),
    )
    np.testing.assert_allclose(
        context.variables["reflected"],
        np.array([1, 0.9, 0.8]),
    )
    np.testing.assert_allclose(
        context.variables["halved"],
        np.array([0, 0.05, 0.1]),
    )
    np.testing.assert_allclose(
        context.variables["powers"],
        np.array([0, 0.01, 0.04]),
    )
    np.testing.assert_array_equal(
        context.variables["mask"],
        np.array([False, False, True]),
    )
    np.testing.assert_array_equal(
        context.variables["negative"],
        np.array([-1, -2, -3]),
    )
    np.testing.assert_allclose(
        context.variables["y"],
        np.sin(2 * np.array([0, 0.1, 0.2])),
    )


def test_interpreter_evaluates_prefixed_integer_literals(execute):
    _, context = execute(
        """
A = 0x2A;
B = 0b101010;
C = 0X2A;
D = 0B101010;
E = 0xff;
F = 0x10 + 0b10;
"""
    )

    assert context.variables["A"] == 42
    assert context.variables["B"] == 42
    assert context.variables["C"] == 42
    assert context.variables["D"] == 42
    assert context.variables["E"] == 255
    assert context.variables["F"] == 18
    assert isinstance(context.variables["A"], int)


def test_interpreter_preserves_typed_integer_literals(execute):
    _, context = execute(
        """
U = 0xFFu8;
S8 = 0xFFs8;
S16 = 0xFFFFs16;
S32 = 0xFFFFFFFFs32;
BU = 0b101010u16;
BS = 0b11111111s8;
uclass = class(U);
sclass = class(S8);
"""
    )

    assert context.variables["U"] == np.uint8(255)
    assert isinstance(context.variables["U"], np.uint8)
    assert context.variables["S8"] == np.int8(-1)
    assert isinstance(context.variables["S8"], np.int8)
    assert context.variables["S16"] == np.int16(-1)
    assert context.variables["S32"] == np.int32(-1)
    assert context.variables["BU"] == np.uint16(42)
    assert context.variables["BS"] == np.int8(-1)
    assert context.variables["uclass"] == "uint8"
    assert context.variables["sclass"] == "int8"


def test_interpreter_supports_prefixed_integer_literals_in_arrays(execute):
    _, context = execute(
        """
A = [0x1 0x2;
     0b11 0b100];
"""
    )

    np.testing.assert_array_equal(
        context.variables["A"],
        np.array([[1, 2], [3, 4]]),
    )


def test_interpreter_evaluates_conditionals_and_loops(execute):
    _, context = execute(
        """
score = 3;

if score > 10
    bucket = 100;
elseif score > 5
    bucket = 50;
else
    bucket = 0;
end

total = 0;
for i = 1:5
    total = total + i;
end

x = 0;
while x < 3
    x = x + 1;
end
"""
    )

    assert context.variables["bucket"] == 0
    assert context.variables["total"] == 15
    assert context.variables["x"] == 3


def test_interpreter_evaluates_matlab_logical_not_and_not_equal(execute):
    _, context = execute(
        """
not_false = ~false;
not_equal = 3 ~= 4;
equal_check = 3 ~= 3;
"""
    )

    assert context.variables["not_false"] is True
    assert context.variables["not_equal"] is True
    assert context.variables["equal_check"] is False


def test_interpreter_constructs_logical_matrices(execute):
    _, context = execute(
        """
T = true(2, 3);
F = false(2, 3);
S = true(2);
row = [true false true];
logical_class = class(T);
""",
        analyze=True,
    )

    np.testing.assert_array_equal(
        context.variables["T"],
        np.ones((2, 3), dtype=bool),
    )
    np.testing.assert_array_equal(
        context.variables["F"],
        np.zeros((2, 3), dtype=bool),
    )
    np.testing.assert_array_equal(
        context.variables["S"],
        np.ones((2, 2), dtype=bool),
    )
    np.testing.assert_array_equal(
        context.variables["row"],
        np.array([True, False, True]),
    )

    assert context.variables["T"].dtype == np.bool_
    assert context.variables["F"].dtype == np.bool_
    assert context.variables["logical_class"] == "logical"


def test_interpreter_supports_who_command(execute):
    result, context = execute(
        """
alpha = 1;
who;
""",
        analyze=True,
    )

    assert result == ["alpha"]
    assert context.variables["ans"] == ["alpha"]


def test_interpreter_handles_vectors_matrices_indexing_and_transpose(execute):
    _, context = execute(
        """
A = [1 2 3];
B = [4 5 6];
C = A.*B;
R1 = 1:3;
R2 = 4:6;
range_product = R1.*R2;

M = [1 2;
     3 4];
N = [5 6;
     7 8];
element_product = M.*N;
picked = M(2,1);
product = M * M;
transpose = M';
"""
    )

    np.testing.assert_array_equal(context.variables["C"], np.array([4, 10, 18]))
    np.testing.assert_array_equal(
        context.variables["range_product"],
        np.array([4, 10, 18]),
    )
    np.testing.assert_array_equal(
        context.variables["element_product"],
        np.array([[5, 12], [21, 32]]),
    )
    assert context.variables["picked"] == 3
    np.testing.assert_array_equal(
        context.variables["product"],
        np.array([[7, 10], [15, 22]]),
    )
    np.testing.assert_array_equal(
        context.variables["transpose"],
        np.array([[1, 3], [2, 4]]),
    )


def test_interpreter_supports_colon_matrix_indexing(execute):
    _, context = execute(
        """
A = [1 2 3; 4 5 6; 7 8 9];
row = A(1, :);
col = A(:, 2);
block = A(1:2, 2:3);
"""
    )

    np.testing.assert_array_equal(
        context.variables["row"],
        np.array([1, 2, 3]),
    )
    np.testing.assert_array_equal(
        context.variables["col"],
        np.array([[2], [5], [8]]),
    )
    np.testing.assert_array_equal(
        context.variables["block"],
        np.array([[2, 3], [5, 6]]),
    )


def test_interpreter_supports_end_keyword_in_indexing(execute):
    _, context = execute(
        """
A = [1 2 3; 4 5 6; 7 8 9];
last = A(end, end);
middle_row = A(end-1, :);
last_col = A(:, end);
tail = A(end-2:end, :);
v = [1 2 3 4 5];
v_last = v(end);
v_middle = v(2:end-1);
"""
    )

    assert context.variables["last"] == 9
    np.testing.assert_array_equal(
        context.variables["middle_row"],
        np.array([4, 5, 6]),
    )
    np.testing.assert_array_equal(
        context.variables["last_col"],
        np.array([[3], [6], [9]]),
    )
    np.testing.assert_array_equal(
        context.variables["tail"],
        np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
    )
    assert context.variables["v_last"] == 5
    np.testing.assert_array_equal(
        context.variables["v_middle"],
        np.array([2, 3, 4]),
    )


def test_interpreter_supports_vector_and_linear_indexing(execute):
    _, context = execute(
        """
A = [1 2 3; 4 5 6; 7 8 9];
rows = A([1 3], :);
cols = A(:, [1 2]);
first = A(1);
third = A(3);
fifth = A(5);
last = A(end);
picked = A([1 5 9]);
"""
    )

    np.testing.assert_array_equal(
        context.variables["rows"],
        np.array([[1, 2, 3], [7, 8, 9]]),
    )
    np.testing.assert_array_equal(
        context.variables["cols"],
        np.array([[1, 2], [4, 5], [7, 8]]),
    )
    assert context.variables["first"] == 1
    assert context.variables["third"] == 7
    assert context.variables["fifth"] == 5
    assert context.variables["last"] == 9
    np.testing.assert_array_equal(
        context.variables["picked"],
        np.array([1, 5, 9]),
    )


def test_interpreter_supports_advanced_indexed_assignment(execute):
    _, context = execute(
        """
A = zeros(3, 3);
A(1, 1) = 5;
single = A(1, 1);
A(2, :) = [10 11 12];
row = A(2, :);
A(1:2, 1:2) = 99;
block = A(1:2, 1:2);
A(:, 3) = 7;
col = A(:, 3);
"""
    )

    assert context.variables["single"] == 5
    np.testing.assert_array_equal(
        context.variables["row"],
        np.array([10, 11, 12]),
    )
    np.testing.assert_array_equal(
        context.variables["block"],
        np.array([[99, 99], [99, 99]]),
    )
    np.testing.assert_array_equal(
        context.variables["col"],
        np.array([[7], [7], [7]]),
    )


def test_interpreter_supports_logical_indexing_and_assignment(execute):
    _, context = execute(
        """
A = [1 2 3; 4 5 6; 7 8 9];
mask = A > 5;
selected = A(mask);
A(A > 5 & A < 9) = 0;
row1 = A(1, :);
row3 = A(3, :);
"""
    )

    np.testing.assert_array_equal(
        context.variables["selected"],
        np.array([[7], [8], [6], [9]]),
    )
    np.testing.assert_array_equal(
        context.variables["row1"],
        np.array([1, 2, 3]),
    )
    np.testing.assert_array_equal(
        context.variables["row3"],
        np.array([0, 0, 9]),
    )


def test_interpreter_supports_flattening_and_stepped_ranges(execute):
    _, context = execute(
        """
A = [1 2 3; 4 5 6];
flat = A(:);
A(:) = 0;
v = [1 2 3 4 5 6 7 8 9 10];
odd = v(1:2:10);
tail = v(end-2:end);
"""
    )

    np.testing.assert_array_equal(
        context.variables["flat"],
        np.array([[1], [4], [2], [5], [3], [6]]),
    )
    np.testing.assert_array_equal(
        context.variables["A"],
        np.zeros((2, 3)),
    )
    np.testing.assert_array_equal(
        context.variables["odd"],
        np.array([1, 3, 5, 7, 9]),
    )
    np.testing.assert_array_equal(
        context.variables["tail"],
        np.array([8, 9, 10]),
    )


def test_interpreter_reports_indexing_errors(execute):
    with pytest.raises(MathToolRuntimeError) as bounds_error:
        execute(
            """
A = [1 2 3; 4 5 6];
x = A(5, 5);
"""
        )

    assert "out of bounds" in str(bounds_error.value)

    with pytest.raises(MathToolRuntimeError) as scalar_error:
        execute(
            """
x = 5;
y = x(1, 1);
"""
        )

    assert "Cannot index scalar" in str(scalar_error.value)


def test_interpreter_rejects_mismatched_elementwise_multiply_sizes(execute):
    with pytest.raises(MathToolRuntimeError) as error:
        execute(
            """
A = [1 2 3];
B = [4 5];
C = A.*B;
"""
        )

    assert "same size" in str(error.value)


def test_interpreter_supports_syms_sym_class_and_ans(execute):
    result, context = execute(
        """
syms x
x;
symbolic_class = class(x);
f1 = sym('x');
f2 = x + 1;
class(f1);
"""
    )

    assert isinstance(context.variables["x"], SymbolicValue)
    assert str(context.variables["x"]) == "x"
    assert context.variables["symbolic_class"] == "sym"
    assert isinstance(context.variables["f1"], SymbolicValue)
    assert str(context.variables["f1"]) == "x"
    assert str(context.variables["f2"]) == "x + 1"
    assert result == "sym"
    assert context.variables["ans"] == "sym"


def test_interpreter_solves_symbolic_equations_and_systems(execute):
    _, context = execute(
        """
syms a b c x
eqn = a*x^2 + b*x + c == 0;
S = solve(eqn);
Sa = solve(eqn, a);
real_roots = solve(x^2 + 1 == 0, x, Real=true);

syms u v
eqns = [2*u + v == 0, u - v == 1];
Y = solve(eqns, [u v]);
Y_auto = solve(eqns);
Y_class = class(Y);
auto_vars = symvar(eqns);
""",
        analyze=True,
    )

    assert str(context.variables["eqn"]) == "a*x^2 + b*x + c == 0"
    assert [
        str(solution)
        for solution in context.variables["S"]
    ] == [
        "(-b - sqrt(-4*a*c + b^2))/(2*a)",
        "(-b + sqrt(-4*a*c + b^2))/(2*a)",
    ]
    assert str(context.variables["Sa"]) == (
        "(-b*x - c)/x^2"
    )
    assert context.variables["real_roots"].size == 0
    assert str(context.variables["Y"]["u"]) == "1/3"
    assert str(context.variables["Y"]["v"]) == "-2/3"
    assert str(context.variables["Y_auto"]["u"]) == "1/3"
    assert str(context.variables["Y_auto"]["v"]) == "-2/3"
    assert context.variables["Y_class"] == "struct"
    assert [
        str(variable)
        for variable in context.variables["auto_vars"]
    ] == ["u", "v"]


def test_interpreter_builds_valid_symbolic_expression_trees(execute):
    _, context = execute(
        """
syms a b c x

exp1 = a^2 + 5*b + 6;
exp2 = (c + b) * (a + 1);
expr = exp1 * exp2;
expanded = expand(expr);
collected = collect(expanded, a);
factored = factor(expanded);
same = simplify(expr - factored);
replaced = subs(expr, a, 2);
coefficients = coeffs(x^2 + 2*x + 1, x);
numeric_factors = factor(60);
""",
        analyze=True,
    )

    assert str(context.variables["expr"]) == (
        "(a + 1)*(b + c)*(a^2 + 5*b + 6)"
    )
    assert "a^3*b" in str(context.variables["expanded"])
    assert "a^3*(b + c)" in str(context.variables["collected"])
    assert str(context.variables["factored"]) == (
        "(a + 1)*(b + c)*(a^2 + 5*b + 6)"
    )
    assert str(context.variables["same"]) == "0"
    assert str(context.variables["replaced"]) == (
        "3*(b + c)*(5*b + 10)"
    )
    assert [
        str(value)
        for value in context.variables["coefficients"]
    ] == ["1", "2", "1"]
    np.testing.assert_array_equal(
        context.variables["numeric_factors"],
        np.array([2, 2, 3, 5]),
    )


def test_interpreter_uses_symbolic_power_precedence_and_associativity(execute):
    _, context = execute(
        """
syms x
symbolic_power = -x^2;
numeric_power = -2^2;
right_assoc = 2^3^2;
"""
    )

    assert str(context.variables["symbolic_power"]) == "-x^2"
    assert context.variables["numeric_power"] == -4
    assert context.variables["right_assoc"] == 512


def test_interpreter_symbolic_variable_can_be_overwritten_by_double(execute):
    _, context = execute(
        """
syms x
x = 1 / 33;
kind = class(x);
"""
    )

    assert context.variables["x"] == pytest.approx(1 / 33)
    assert context.variables["kind"] == "double"


def test_interpreter_supports_symbolic_diff_int_and_math_dispatch(execute):
    _, context = execute(
        """
x = sym("x");
f = sin(x^2);
df = diff(f, x);
d4 = diff(x^6, x, 4);
F = int(x^2, x);
q = int(sin(x), x, 0, pi);
syms("y");
mixed = diff(x*sin(x*y), x, y);
""",
        analyze=True,
    )

    assert str(context.variables["df"]) == "2*x*cos(x^2)"
    assert str(context.variables["d4"]) == "360*x^2"
    assert str(context.variables["F"]) == "x^3/3"
    assert str(context.variables["q"]) == "2"
    assert isinstance(context.variables["y"], SymbolicValue)
    assert "cos(x*y)" in str(context.variables["mixed"])


def test_interpreter_supports_symbolic_matrix_differentiation(execute):
    _, context = execute(
        """
x = sym("x");
A = [x x^2; sin(x) cos(x)];
dA = diff(A, x);
""",
        analyze=True,
    )

    assert [
        [str(value) for value in row]
        for row in context.variables["dA"]
    ] == [
        ["1", "2*x"],
        ["cos(x)", "-sin(x)"],
    ]


def test_interpreter_supports_function_handles_and_numerical_integrals(execute):
    _, context = execute(
        """
f = @(x) exp(-x.^2);
q = integral(f, 0, 1);
c = 5;
closed = @(x) x + c;
c = 20;
closed_value = closed(1);
g = @(x,y) x.^2 + y.^2;
q2 = integral2(g, 0, 1, 0, 1);
ymax = @(x) 1 - x;
tri = integral2(@(x,y) x + y, 0, 1, 0, ymax);
kind = class(f);
direct = f(2);
""",
        analyze=True,
    )

    assert context.variables["q"] == pytest.approx(
        0.746824,
        rel=1e-5,
    )
    assert context.variables["q2"] == pytest.approx(
        2 / 3,
        rel=1e-5,
    )
    assert context.variables["tri"] == pytest.approx(
        1 / 3,
        rel=1e-5,
    )
    assert context.variables["kind"] == "function_handle"
    assert context.variables["direct"] == pytest.approx(
        np.exp(-4)
    )
    assert context.variables["closed_value"] == 6


def test_interpreter_supports_trapz_gradient_and_multi_output(execute):
    _, context = execute(
        """
Y = [1 4 9 16 25];
Q = trapz(Y);
x = 1:10;
gx = gradient(x);
M = [1 2 3; 4 5 6];
[FX, FY] = gradient(M);
row_area = trapz(M, 2);
""",
        analyze=True,
    )

    assert context.variables["Q"] == pytest.approx(42)
    np.testing.assert_allclose(
        context.variables["gx"],
        np.ones(10),
    )
    np.testing.assert_allclose(
        context.variables["FX"],
        np.ones((2, 3)),
    )
    np.testing.assert_allclose(
        context.variables["FY"],
        np.full((2, 3), 3),
    )
    np.testing.assert_allclose(
        context.variables["row_area"],
        np.array([4, 10]),
    )


def test_interpreter_supports_matlab_style_input(execute):
    context = RuntimeContext()
    responses = iter([
        "base + 2",
        "hello there",
        "",
        "not valid",
        "41",
    ])
    output = []

    context.input_callback = lambda prompt: next(responses)
    context.output_callback = output.append

    _, context = execute(
        """
base = 40;
x = input("value? ");
txt = input("text? ", "s");
empty = input("empty? ");
retry = input("retry? ");
""",
        context=context,
        analyze=True,
    )

    assert context.variables["x"] == 42
    assert context.variables["txt"] == "hello there"
    assert context.variables["empty"].size == 0
    assert context.variables["retry"] == 41
    assert any(
        "Undefined" in message
        for message in output
    )


def test_interpreter_automatic_output_semicolon_and_ans_behavior(execute):
    context = RuntimeContext()
    output = []
    context.output_callback = output.append

    _, context = execute(
        """
A = 5;
A
A + 2;
ans + 4
B = A + 2
C = A + 2.5;
D = A / 2;
disp(A);
""",
        context=context,
    )

    assert isinstance(context.variables["A"], int)
    assert isinstance(context.variables["B"], int)
    assert isinstance(context.variables["C"], float)
    assert context.variables["D"] == pytest.approx(2.5)
    assert context.variables["ans"] == 11
    assert output == [
        "5\n\n",
        "11\n\n",
        "B =\n\n    7\n\n",
        "5\n\n",
    ]


def test_interpreter_clean_integer_matrix_display_and_types(execute):
    context = RuntimeContext()
    output = []
    context.output_callback = output.append

    _, context = execute(
        """
A = [1 2; 3 4];
B = A + 1;
C = A / 2;
disp(A);
disp([1.5 2.5; 3.5 4.5]);
""",
        context=context,
    )

    assert np.issubdtype(context.variables["A"].dtype, np.integer)
    assert np.issubdtype(context.variables["B"].dtype, np.integer)
    assert np.issubdtype(context.variables["C"].dtype, np.floating)
    assert output[0] == "[[1 2]\n [3 4]]\n\n"
    assert output[1] == "[[1.5 2.5]\n [3.5 4.5]]\n\n"


def test_interpreter_sym_preserves_exact_text(execute):
    _, context = execute(
        """
x = sym('1/33');
kind = class(x);
x;
"""
    )

    assert isinstance(context.variables["x"], SymbolicValue)
    assert str(context.variables["x"]) == "1/33"
    assert context.variables["kind"] == "sym"
    assert context.variables["ans"] == context.variables["x"]


def test_interpreter_assigns_vector_and_matrix_elements(execute):
    _, context = execute(
        """
M = [1 2;
     3 4];
M(1,1) = 5;
M(2,2) = M(1,1) + 1;
picked = M(2,2);

v = [1 2 3];
v(2) = 9;
"""
    )

    np.testing.assert_array_equal(
        context.variables["M"],
        np.array([[5, 2], [3, 6]]),
    )
    assert context.variables["picked"] == 6
    np.testing.assert_array_equal(
        context.variables["v"],
        np.array([1, 9, 3]),
    )


def test_interpreter_supports_basic_struct_field_assignment(execute):
    _, context = execute(
        """
s.name = 'Alice';
s.age = 30;
x = s.name;
y = s.age;
"""
    )

    assert context.variables["s"]["name"] == "Alice"
    assert context.variables["s"]["age"] == 30
    assert context.variables["x"] == "Alice"
    assert context.variables["y"] == 30


def test_interpreter_supports_nested_struct_assignment(execute):
    _, context = execute(
        """
user.name = 'Bob';
user.address.city = 'Boston';
user.address.zip = 2108;
city = user.address.city;
zipCode = user.address.zip;
"""
    )

    assert context.variables["user"]["name"] == "Bob"
    assert context.variables["user"]["address"]["city"] == "Boston"
    assert context.variables["city"] == "Boston"
    assert context.variables["zipCode"] == 2108


def test_interpreter_overwrites_struct_fields(execute):
    _, context = execute(
        """
s.x = 1;
s.x = 2;
y = s.x;
"""
    )

    assert context.variables["s"]["x"] == 2
    assert context.variables["y"] == 2


def test_interpreter_supports_struct_constructor_and_empty_struct(execute):
    _, context = execute(
        """
p = struct('name', 'Alice', 'age', 30);
n = p.name;
a = p.age;

s = struct();
s.x = 5;
y = s.x;
kind = class(s);
"""
    )

    assert context.variables["p"]["name"] == "Alice"
    assert context.variables["p"]["age"] == 30
    assert context.variables["n"] == "Alice"
    assert context.variables["a"] == 30
    assert context.variables["s"]["x"] == 5
    assert context.variables["y"] == 5
    assert context.variables["kind"] == "struct"


def test_interpreter_supports_nested_struct_constructor(execute):
    _, context = execute(
        """
user = struct('address', struct('city', 'Boston'));
city = user.address.city;
"""
    )

    assert context.variables["user"]["address"]["city"] == "Boston"
    assert context.variables["city"] == "Boston"


def test_interpreter_raises_for_missing_struct_field(execute):
    with pytest.raises(MathToolRuntimeError) as error:
        execute(
            """
s = struct('a', 1);
x = s.b;
"""
        )

    assert "Reference to non-existent field 'b'" in str(error.value)


def test_interpreter_raises_for_non_struct_dot_access(execute):
    with pytest.raises(MathToolRuntimeError) as error:
        execute(
            """
x = 5;
y = x.name;
"""
        )

    assert "non-struct" in str(error.value)


def test_interpreter_raises_for_invalid_struct_constructor_arguments(execute):
    with pytest.raises(MathToolRuntimeError) as odd_error:
        execute("s = struct('a');")

    assert "name/value pairs" in str(odd_error.value)

    with pytest.raises(MathToolRuntimeError) as name_error:
        execute("s = struct(123, 456);")

    assert "field names must be strings" in str(name_error.value)


def test_interpreter_supports_struct_fields_in_expressions_and_indexing(execute):
    _, context = execute(
        """
s.x = 10;
s.grades = [95 88 91];
y = s.x + 5;
z = s.grades(2);
avgGrade = mean(s.grades);
"""
    )

    assert context.variables["y"] == 15
    assert context.variables["z"] == 88
    assert context.variables["avgGrade"] == pytest.approx(91.3333333333)


def test_interpreter_supports_struct_arrays(execute):
    _, context = execute(
        """
students(1).name = 'Alice';
students(1).grade = 95;
students(2).name = 'Bob';
students(2).grade = 88;
first = students(1).name;
secondGrade = students(2).grade;
"""
    )

    assert context.variables["students"][0]["name"] == "Alice"
    assert context.variables["students"][1]["name"] == "Bob"
    assert context.variables["first"] == "Alice"
    assert context.variables["secondGrade"] == 88


def test_interpreter_struct_support_preserves_decimal_and_elementwise_ops(execute):
    _, context = execute(
        """
x = 3.14;
y = x + 1;
A = [1 2 3];
B = A .* 2;
"""
    )

    assert context.variables["y"] == pytest.approx(4.14)
    np.testing.assert_array_equal(
        context.variables["B"],
        np.array([2, 4, 6]),
    )


def test_interpreter_supports_matrix_builtins(execute):
    _, context = execute(
        """
M = [1 2;
     3 4];
d = det(M);
i = inv(M);
s = size(M);
u = sum(M);
v = mean(M);
mx = max(M);
mn = min(M);
e = eye(3);
z1 = zeros(3);
z2 = zeros(2, 4);
o1 = ones(3);
o2 = ones(2, 4);
"""
    )

    assert context.variables["d"] == -2.0
    np.testing.assert_allclose(
        context.variables["i"],
        np.array([[-2.0, 1.0], [1.5, -0.5]]),
    )
    np.testing.assert_array_equal(
        context.variables["s"],
        np.array([2, 2]),
    )
    assert context.variables["u"] == 10
    assert context.variables["v"] == 2.5
    assert context.variables["mx"] == 4
    assert context.variables["mn"] == 1
    np.testing.assert_array_equal(context.variables["e"], np.eye(3))
    np.testing.assert_array_equal(context.variables["z1"], np.zeros((3, 3)))
    np.testing.assert_array_equal(context.variables["z2"], np.zeros((2, 4)))
    np.testing.assert_array_equal(context.variables["o1"], np.ones((3, 3)))
    np.testing.assert_array_equal(context.variables["o2"], np.ones((2, 4)))


def test_interpreter_supports_engineering_numpy_inspired_builtins(execute):
    _, context = execute(
        """
t = linspace(0, 1, 5);
A = reshape(1:4, 2, 2);
stats_prod = prod(1:4);
stats_median = median(1:4);
stats_p50 = percentile(1:4, 50);
x = linsolve([3 1; 1 2], [9; 8]);
p = polyval([1 0 -1], 3);
f = fft([1 0 0 0]);
round_trip = allclose(ifft(f), [1 0 0 0]);
r = roots([1 0 -1]);
"""
    )

    np.testing.assert_allclose(
        context.variables["t"],
        np.linspace(0, 1, 5),
    )
    np.testing.assert_array_equal(
        context.variables["A"],
        np.array([[1, 2], [3, 4]]),
    )
    assert context.variables["stats_prod"] == 24
    assert context.variables["stats_median"] == 2.5
    assert context.variables["stats_p50"] == 2.5
    np.testing.assert_allclose(
        context.variables["x"],
        np.array([[2], [3]]),
    )
    assert context.variables["p"] == 8
    np.testing.assert_allclose(
        context.variables["f"],
        np.array([1, 1, 1, 1]),
    )
    assert context.variables["round_trip"] is True
    np.testing.assert_allclose(
        np.sort(context.variables["r"]),
        np.array([-1, 1]),
    )


def test_interpreter_supports_matlab_style_complex_numbers(execute):
    _, context = execute(
        """
z = 1 + 2i;
w = 3 - 4j;
unit_i = i;
unit_j = j;
s = sqrt(-1);
c = complex(5, -6);
r = 4;
theta = pi/4;
polar = r * exp(1i * theta);
x = [1:4]';
y = [8:-2:2]';
column = x + 1i * y;
""",
        analyze=True,
    )

    assert context.variables["z"] == 1 + 2j
    assert context.variables["w"] == 3 - 4j
    assert context.variables["unit_i"] == 1j
    assert context.variables["unit_j"] == 1j
    assert context.variables["s"] == 1j
    assert context.variables["c"] == 5 - 6j
    assert context.variables["polar"] == pytest.approx(
        4 * np.exp(1j * np.pi / 4)
    )
    np.testing.assert_allclose(
        context.variables["column"],
        np.array(
            [
                [1 + 8j],
                [2 + 6j],
                [3 + 4j],
                [4 + 2j],
            ]
        ),
    )


def test_interpreter_supports_complex_number_helper_functions(execute):
    _, context = execute(
        """
z = 1 + 2i;
values = [1+2i 3-4j];
phase = angle(z);
phases = angle(values);
z_conj = conj(z);
values_conj = conj(values);
z_real = real(z);
z_imag = imag(z);
values_real = real(values);
values_imag = imag(values);
plain_is_real = isreal([1 2 3]);
complex_is_real = isreal(values);
zero_imag_is_real = isreal(complex(1, 0));
""",
        analyze=True,
    )

    assert context.variables["phase"] == pytest.approx(
        np.angle(1 + 2j)
    )
    np.testing.assert_allclose(
        context.variables["phases"],
        np.angle(np.array([1 + 2j, 3 - 4j])),
    )
    assert context.variables["z_conj"] == 1 - 2j
    np.testing.assert_allclose(
        context.variables["values_conj"],
        np.array([1 - 2j, 3 + 4j]),
    )
    assert context.variables["z_real"] == 1
    assert context.variables["z_imag"] == 2
    np.testing.assert_array_equal(
        context.variables["values_real"],
        np.array([1, 3]),
    )
    np.testing.assert_array_equal(
        context.variables["values_imag"],
        np.array([2, -4]),
    )
    assert context.variables["plain_is_real"] is True
    assert context.variables["complex_is_real"] is False
    assert context.variables["zero_imag_is_real"] is False


def test_interpreter_supports_implicit_and_explicit_function_returns(execute):
    _, context = execute(
        """
function y = square(x)
    y = x ^ 2;
end

function y = first_positive(x)
    if x > 0
        return x;
    end
    y = 0;
end

A = square(5);
B = first_positive(9);
"""
    )

    assert context.variables["A"] == 25
    assert context.variables["B"] == 9
    assert context.call_stack.format_stack() == ""


def test_interpreter_supports_matlab_style_multi_output_functions(execute):
    _, context = execute(
        """
function [m, s] = stat(x)
    n = length(x);
    m = sum(x) / n;
    s = sqrt(sum((x - m) .^ 2 / n));
end

values = [12.7, 45.4, 98.9, 26.6, 53.1];
[ave, stdev] = stat(values);
first = stat(values);
""",
        analyze=True,
    )

    assert context.variables["ave"] == pytest.approx(47.34)
    assert context.variables["stdev"] == pytest.approx(
        29.4124,
        rel=1e-5,
    )
    assert context.variables["first"] == pytest.approx(47.34)


def test_interpreter_rejects_too_many_requested_function_outputs(execute):
    with pytest.raises(MathToolRuntimeError) as error:
        execute(
            """
function [a, b] = pair()
    a = 1;
    b = 2;
end

[x, y, z] = pair();
"""
        )

    assert "were requested" in str(error.value)


def test_interpreter_bare_return_exits_function(execute):
    _, context = execute(
        """
function y = clamp_positive(x)
    y = 0;

    if x > 0
        y = x;
        return
    end

    y = -1;
end

positive = clamp_positive(6);
negative = clamp_positive(-2);
""",
        analyze=True,
    )

    assert context.variables["positive"] == 6
    assert context.variables["negative"] == -1


def test_interpreter_supports_break_and_continue_in_for_loops(execute):
    _, context = execute(
        """
total = 0;

for i = 1:6
    if i == 2
        continue;
    end

    if i == 5
        break;
    end

    total = total + i;
end
""",
        analyze=True,
    )

    assert context.variables["total"] == 8


def test_interpreter_supports_break_and_continue_in_while_loops(execute):
    _, context = execute(
        """
x = 0;
total = 0;

while x < 6
    x = x + 1;

    if x == 2
        continue;
    end

    if x == 5
        break;
    end

    total = total + x;
end
""",
        analyze=True,
    )

    assert context.variables["x"] == 5
    assert context.variables["total"] == 8


def test_interpreter_break_only_exits_nearest_loop(execute):
    _, context = execute(
        """
total = 0;

for outer = 1:3
    for inner = 1:3
        if inner == 2
            break;
        end

        total = total + outer;
    end
end
""",
        analyze=True,
    )

    assert context.variables["total"] == 6


def test_interpreter_rejects_break_from_function_called_inside_loop(execute):
    with pytest.raises(MathToolRuntimeError) as error:
        execute(
            """
function y = bad()
    break;
    y = 1;
end

for i = 1:3
    value = bad();
end
"""
        )

    assert "'break' can only be used inside a loop" in str(
        error.value
    )


def test_interpreter_rejects_continue_from_function_called_inside_loop(execute):
    with pytest.raises(MathToolRuntimeError) as error:
        execute(
            """
function y = bad()
    continue;
    y = 1;
end

for i = 1:3
    value = bad();
end
"""
        )

    assert "'continue' can only be used inside a loop" in str(
        error.value
    )


def test_interpreter_sends_console_output_to_callback(execute):
    context = RuntimeContext()
    output = []
    context.output_callback = output.append

    execute(
        """
disp("answer");
fprintf("count=%d pi=%.2f\\n", 42, pi);
warning("value %.1f is unusually high", 9.5);
""",
        context=context,
    )

    assert output == [
        "answer\n\n",
        "count=42 pi=3.14\n",
        "Warning: value 9.5 is unusually high\n",
    ]


def test_interpreter_error_aborts_execution(execute):
    context = RuntimeContext()
    output = []
    context.output_callback = output.append

    with pytest.raises(Exception) as raised:
        execute(
            """
error("File %s not found after %d attempts", "data.csv", 3);
A = 1;
""",
            context=context,
        )

    assert output == [
        "Error: File data.csv not found after 3 attempts\n"
    ]
    assert str(raised.value) == (
        "Error: File data.csv not found after 3 attempts"
    )


def test_interpreter_supports_help_command_and_function_call(execute):
    result, _ = execute("help eig;")

    assert "Definition: Eigenvalue decomposition" in result
    assert "Syntax:" in result
    assert "eig(A)" in result
    assert "Inputs:" in result
    assert "Output:" in result
    assert "Options:" in result

    result, _ = execute("help('linspace');")

    assert "Create linearly spaced points" in result
    assert "linspace(start, stop, num)" in result

    result, _ = execute("help bode;")

    assert "Plot Bode magnitude and phase" in result
    assert "bode(num, den, w)" in result

    context = RuntimeContext()
    output = []
    context.output_callback = output.append

    result, _ = execute(
        "help missing_topic;",
        context=context,
    )

    assert result is None
    assert "No help available for missing_topic" in output[0]


def test_interpreter_supports_lookfor_command(tmp_path, execute):
    (tmp_path / "squareNumber.m").write_text(
        """
function y = squareNumber(x)
% SQUARENUMBER Squares the input value.
%
%   y = SQUARENUMBER(x) returns x squared.
    y = x ^ 2;
end
""",
        encoding="utf-8",
    )

    context = RuntimeContext()
    context.set_current_working_directory(tmp_path)
    output = []
    context.output_callback = output.append

    result, _ = execute(
        "lookfor squared;",
        context=context,
    )

    assert result is None
    assert (
        "squareNumber - SQUARENUMBER Squares the input value."
        in output[0]
    )


def test_interpreter_supports_cwd_command_and_function(tmp_path, execute):
    context = RuntimeContext()
    context.set_current_working_directory(tmp_path)

    result, _ = execute(
        """
cwd;
value = cwd();
""",
        context=context,
    )

    assert result == str(tmp_path.resolve())
    assert context.variables["value"] == str(
        tmp_path.resolve()
    )


def test_interpreter_raises_domain_runtime_errors(execute):
    with pytest.raises(MathToolRuntimeError) as error:
        execute("A = 5 / 0;")

    assert "Division by zero" in str(error.value)
