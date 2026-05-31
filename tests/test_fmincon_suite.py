import numpy as np
import pytest

from core.errors.errors import RuntimeError as MathToolRuntimeError
from core.runtime.context import RuntimeContext


def test_fmincon_solves_unconstrained_quadratic(execute):
    _, context = execute(
        """
fun = @(x) (x(1)-3)^2 + (x(2)-2)^2;
x0 = [0 0];
x = fmincon(fun, x0);
"""
    )

    np.testing.assert_allclose(
        context.variables["x"],
        np.array([3.0, 2.0]),
        atol=1e-5,
    )


def test_fmincon_solves_bound_constrained_quadratic(execute):
    _, context = execute(
        """
fun = @(x) (x(1)-3)^2 + (x(2)-2)^2;
x0 = [0 0];
lb = [0 0];
ub = [1 1];
x = fmincon(fun, x0, [], [], [], [], lb, ub);
"""
    )

    np.testing.assert_allclose(
        context.variables["x"],
        np.array([1.0, 1.0]),
        atol=1e-5,
    )


def test_fmincon_supports_linear_inequality(execute):
    _, context = execute(
        """
fun = @(x) 100*(x(2)-x(1)^2)^2 + (1-x(1))^2;
x0 = [-1 2];
A = [1 2];
b = 1;
x = fmincon(fun, x0, A, b);
constraint_value = A*x';
"""
    )

    assert context.variables["constraint_value"] <= 1 + 1e-6


def test_fmincon_supports_linear_equality_and_inequality(execute):
    _, context = execute(
        """
fun = @(x) 100*(x(2)-x(1)^2)^2 + (1-x(1))^2;
x0 = [0.5 0];
A = [1 2];
b = 1;
Aeq = [2 1];
beq = 1;
x = fmincon(fun, x0, A, b, Aeq, beq);
ineq_value = A*x';
eq_value = Aeq*x';
"""
    )

    assert context.variables["ineq_value"] <= 1 + 1e-6
    assert context.variables["eq_value"] == pytest.approx(1.0, abs=1e-6)


def test_fmincon_supports_nonlinear_constraint(execute):
    _, context = execute(
        """
fun = @(x) 100*(x(2)-x(1)^2)^2 + (1-x(1))^2;
nonlcon = @(x) [((x(1)-1/3)^2 + (x(2)-1/3)^2 - (1/3)^2), []];
x0 = [0.25 0.25];
lb = [0 0.2];
ub = [0.5 0.8];
x = fmincon(fun, x0, [], [], [], [], lb, ub, nonlcon);
circle_value = (x(1)-1/3)^2 + (x(2)-1/3)^2 - (1/3)^2;
"""
    )

    x = context.variables["x"]
    assert np.all(x >= np.array([0.0, 0.2]) - 1e-6)
    assert np.all(x <= np.array([0.5, 0.8]) + 1e-6)
    assert context.variables["circle_value"] <= 1e-6


def test_fmincon_options_display_iter(execute):
    output = []
    context = RuntimeContext()
    context.output_callback = output.append

    _, context = execute(
        """
fun = @(x) 100*(x(2)-x(1)^2)^2 + (1-x(1))^2;
x0 = [0 0];
options = optimoptions("fmincon", "Display", "iter", "Algorithm", "sqp");
x = fmincon(fun, x0, [], [], [], [], [], [], [], options);
""",
        context=context,
    )

    np.testing.assert_allclose(
        context.variables["x"],
        np.array([1.0, 1.0]),
        atol=1e-4,
    )
    assert any("Iter" in item for item in output)
    assert any("SLSQP" in item for item in output)


def test_fmincon_returns_full_output(execute):
    _, context = execute(
        """
fun = @(x) (x(1)-3)^2 + (x(2)-2)^2;
x0 = [0 0];
result = fmincon(fun, x0, "FullOutput", true);
x = result.x;
fval = result.fval;
iterations = result.output.iterations;
"""
    )

    np.testing.assert_allclose(
        context.variables["x"],
        np.array([3.0, 2.0]),
        atol=1e-5,
    )
    assert context.variables["fval"] == pytest.approx(0.0, abs=1e-8)
    assert context.variables["iterations"] >= 1


def test_fmincon_rejects_inconsistent_bounds(execute):
    with pytest.raises(MathToolRuntimeError, match="lower bound"):
        execute(
            """
fun = @(x) x(1)^2;
x0 = [0];
lb = [2];
ub = [1];
x = fmincon(fun, x0, [], [], [], [], lb, ub);
"""
        )


def test_fmincon_rejects_vector_objective(execute):
    with pytest.raises(MathToolRuntimeError, match="objective"):
        execute(
            """
fun = @(x) [x(1), x(1)^2];
x0 = [1];
x = fmincon(fun, x0);
"""
        )


def test_fmincon_accepts_problem_structure(execute):
    _, context = execute(
        """
problem.objective = @(x) (x(1)-3)^2 + (x(2)-2)^2;
problem.x0 = [0 0];
problem.lb = [0 0];
problem.ub = [10 10];
problem.solver = "fmincon";
problem.options = optimoptions("fmincon", "Display", "final");
x = fmincon(problem);
"""
    )

    np.testing.assert_allclose(
        context.variables["x"],
        np.array([3.0, 2.0]),
        atol=1e-5,
    )


def test_fmincon_preserves_matrix_shape(execute):
    _, context = execute(
        """
fun = @(X) sum(X.^2);
x0 = [1 2; 3 4];
x = fmincon(fun, x0);
shape = size(x);
"""
    )

    assert tuple(context.variables["x"].shape) == (2, 2)
    np.testing.assert_allclose(context.variables["x"], np.zeros((2, 2)), atol=1e-5)
