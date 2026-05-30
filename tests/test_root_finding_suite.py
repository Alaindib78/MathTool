import numpy as np
import pytest

from core.errors.errors import RuntimeError as MathToolRuntimeError
from core.runtime.context import RuntimeContext


def test_fzero_solves_bracketed_interval(execute):
    _, context = execute(
        """
f = @(x) cos(x);
root = fzero(f, [1 2]);
"""
    )

    assert context.variables["root"] == pytest.approx(
        np.pi / 2,
        rel=0,
        abs=1e-10,
    )


def test_fzero_searches_bracket_from_scalar_start(execute):
    _, context = execute(
        """
f = @(x) sin(x);
root = fzero(f, 3);
"""
    )

    assert context.variables["root"] == pytest.approx(
        np.pi,
        rel=0,
        abs=1e-10,
    )


def test_fzero_solves_parameterized_function_handle(execute):
    _, context = execute(
        """
c = 2;
myfun = @(x,c) cos(c*x);
f = @(x) myfun(x,c);
root = fzero(f, 0.1);
"""
    )

    assert context.variables["root"] == pytest.approx(
        np.pi / 4,
        rel=0,
        abs=1e-10,
    )


def test_fzero_rejects_interval_without_sign_change(execute):
    with pytest.raises(MathToolRuntimeError, match="sign change"):
        execute(
            """
f = @(x) x^2;
root = fzero(f, [-1 1]);
"""
        )


def test_fzero_display_iter_writes_iteration_table(execute):
    output = []
    context = RuntimeContext()
    context.output_callback = output.append

    _, context = execute(
        """
f = @(x) exp(-exp(-x)) - x;
root = fzero(f, [0 1], "Display", "iter");
""",
        context=context,
    )

    assert context.variables["root"] == pytest.approx(
        0.56714329,
        rel=0,
        abs=1e-7,
    )
    assert any("Iter" in item for item in output)
    assert any("brent" in item or "initial" in item for item in output)


def test_newtons_method_solves_polynomial(execute):
    _, context = execute(
        """
f = @(x) x^3 - 2*x - 5;
df = @(x) 3*x^2 - 2;
root = newtons_method(f, df, 2);
"""
    )

    assert context.variables["root"] == pytest.approx(
        2.0945514815,
        rel=0,
        abs=1e-10,
    )


def test_newtons_method_detects_zero_derivative(execute):
    with pytest.raises(MathToolRuntimeError, match="derivative"):
        execute(
            """
f = @(x) x^3;
df = @(x) 3*x^2;
root = newtons_method(f, df, 0);
"""
        )


def test_secant_solves_polynomial(execute):
    _, context = execute(
        """
f = @(x) x^3 - 2*x - 5;
root = secant(f, 1, 3);
"""
    )

    assert context.variables["root"] == pytest.approx(
        2.0945514815,
        rel=0,
        abs=1e-10,
    )


def test_secant_detects_small_denominator(execute):
    with pytest.raises(MathToolRuntimeError, match="denominator"):
        execute(
            """
f = @(x) 1;
root = secant(f, 0, 1);
"""
        )


def test_root_finders_return_full_output_struct(execute):
    _, context = execute(
        """
f = @(x) x^3 - 2*x - 5;
df = @(x) 3*x^2 - 2;
result = newtons_method(f, df, 2, "ReturnAll", true, "FullOutput", true);
root = result.root;
iters = result.output.iterations;
"""
    )

    assert context.variables["root"] == pytest.approx(
        2.0945514815,
        rel=0,
        abs=1e-10,
    )
    assert context.variables["iters"] > 0
