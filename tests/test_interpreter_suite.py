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


def test_interpreter_sends_print_output_to_callback(execute):
    context = RuntimeContext()
    output = []
    context.output_callback = output.append

    execute(
        """
print("answer", 42);
println("done");
""",
        context=context,
    )

    assert output == ["answer 42.0", "done"]


def test_interpreter_raises_domain_runtime_errors(execute):
    with pytest.raises(MathToolRuntimeError) as error:
        execute("A = 5 / 0;")

    assert "Division by zero" in str(error.value)
