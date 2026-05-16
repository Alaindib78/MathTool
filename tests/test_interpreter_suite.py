import numpy as np
import pytest

from core.errors.errors import RuntimeError as MathToolRuntimeError
from core.runtime.context import RuntimeContext


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


def test_interpreter_handles_vectors_matrices_indexing_and_transpose(execute):
    _, context = execute(
        """
A = [1 2 3];
B = [4 5 6];
C = A .* B;

M = [1 2;
     3 4];
picked = M(2,1);
product = M * M;
transpose = M';
"""
    )

    np.testing.assert_array_equal(context.variables["C"], np.array([4, 10, 18]))
    assert context.variables["picked"] == 3
    np.testing.assert_array_equal(
        context.variables["product"],
        np.array([[7, 10], [15, 22]]),
    )
    np.testing.assert_array_equal(
        context.variables["transpose"],
        np.array([[1, 3], [2, 4]]),
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
