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

    assert str(context.variables["eqn"]) == (
        "a * x ^ 2 + b * x + c == 0"
    )
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
        "answer\n",
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
