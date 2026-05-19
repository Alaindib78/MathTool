import numpy as np
import pytest

from core.plotting.engine import PlotEngine
from core.runtime.context import RuntimeContext


class FakePlotEngine:
    def __init__(self):
        self.calls = []

    def plot(self, x, y):
        self.calls.append(("plot", x, y))

    def title(self, text):
        self.calls.append(("title", text))

    def xlabel(self, text):
        self.calls.append(("xlabel", text))

    def ylabel(self, text):
        self.calls.append(("ylabel", text))

    def grid_on(self):
        self.calls.append(("grid_on",))

    def grid_off(self):
        self.calls.append(("grid_off",))


def test_math_builtins_are_vectorized():
    context = RuntimeContext()
    values = np.array([0, np.pi / 2])

    sin = context.functions.get("sin")
    sqrt = context.functions.get("sqrt")
    zeros = context.functions.get("zeros")
    ones = context.functions.get("ones")
    length = context.functions.get("length")
    eye = context.functions.get("eye")
    det = context.functions.get("det")
    inv = context.functions.get("inv")
    size = context.functions.get("size")
    sum_ = context.functions.get("sum")
    mean = context.functions.get("mean")
    max_ = context.functions.get("max")
    min_ = context.functions.get("min")

    np.testing.assert_allclose(sin(context, values), np.array([0, 1]))
    np.testing.assert_array_equal(sqrt(context, np.array([4, 9])), np.array([2, 3]))
    np.testing.assert_array_equal(zeros(context, 3), np.zeros((3, 3)))
    np.testing.assert_array_equal(zeros(context, 2, 4), np.zeros((2, 4)))
    np.testing.assert_array_equal(ones(context, 3), np.ones((3, 3)))
    np.testing.assert_array_equal(ones(context, 2, 4), np.ones((2, 4)))
    assert length(context, values) == 2
    np.testing.assert_array_equal(eye(context, 3), np.eye(3))
    assert det(context, np.array([[1, 2], [3, 4]])) == -2.0
    np.testing.assert_allclose(
        inv(context, np.array([[1.0, 2.0], [3.0, 4.0]])),
        np.array([[-2.0, 1.0], [1.5, -0.5]]),
    )
    np.testing.assert_array_equal(size(context, np.array([[1, 2], [3, 4]])), np.array([2, 2]))
    assert size(context, np.array([1, 2, 3]), 1) == 3
    assert size(context, np.array([1, 2, 3]), 2) == 1
    assert sum_(context, np.array([1, 2, 3])) == 6
    assert mean(context, np.array([1, 2, 3])) == 2
    assert max_(context, np.array([1, 5, 3])) == 5
    assert min_(context, np.array([1, 5, 3])) == 1


def test_engineering_elementwise_and_shape_builtins():
    context = RuntimeContext()
    functions = context.functions

    np.testing.assert_allclose(
        functions.get("asin")(context, np.array([0, 1])),
        np.array([0, np.pi / 2]),
    )
    assert functions.get("atan2")(context, 1, 1) == pytest.approx(
        np.pi / 4
    )
    np.testing.assert_allclose(
        functions.get("rad2deg")(context, np.array([0, np.pi])),
        np.array([0, 180]),
    )
    np.testing.assert_array_equal(
        functions.get("linspace")(context, 0, 1, 5),
        np.linspace(0, 1, 5),
    )
    np.testing.assert_array_equal(
        functions.get("arange")(context, 1, 6, 2),
        np.array([1, 3, 5]),
    )

    matrix = np.array([[1, 2, 3], [4, 5, 6]])

    assert functions.get("numel")(context, matrix) == 6
    assert functions.get("ndims")(context, matrix) == 2
    assert functions.get("isempty")(context, np.array([])) is True
    np.testing.assert_array_equal(
        functions.get("reshape")(context, np.arange(6), 2, 3),
        matrix - 1,
    )
    np.testing.assert_array_equal(
        functions.get("flatten")(context, matrix),
        np.array([1, 2, 3, 4, 5, 6]),
    )
    np.testing.assert_array_equal(
        functions.get("diag")(context, np.array([1, 2, 3])),
        np.diag([1, 2, 3]),
    )
    np.testing.assert_array_equal(
        functions.get("triu")(context, matrix),
        np.triu(matrix),
    )


def test_engineering_statistics_logical_and_signal_builtins():
    context = RuntimeContext()
    functions = context.functions

    values = np.array([1, 2, 3, 4])

    assert functions.get("prod")(context, values) == 24
    assert functions.get("median")(context, values) == 2.5
    assert functions.get("std")(context, values) == pytest.approx(
        np.std(values)
    )
    assert functions.get("var")(context, values) == pytest.approx(
        np.var(values)
    )
    assert functions.get("percentile")(context, values, 50) == 2.5
    assert functions.get("any")(context, np.array([0, 1])) is True
    assert functions.get("all")(context, np.array([1, 1])) is True
    np.testing.assert_array_equal(
        functions.get("isfinite")(context, np.array([1, np.inf])),
        np.array([True, False]),
    )
    assert functions.get("allclose")(
        context,
        np.array([1.0, 2.0]),
        np.array([1.0, 2.0 + 1e-9]),
    ) is True

    np.testing.assert_array_equal(
        functions.get("diff")(context, values),
        np.array([1, 1, 1]),
    )
    np.testing.assert_array_equal(
        functions.get("cumsum")(context, values),
        np.array([1, 3, 6, 10]),
    )
    assert functions.get("trapz")(context, np.array([0, 1, 2])) == 2.0
    assert functions.get("interp1")(
        context,
        np.array([0, 1, 2]),
        np.array([0, 10, 20]),
        1.5,
    ) == 15.0


def test_engineering_linalg_fft_polynomial_and_random_builtins():
    context = RuntimeContext()
    functions = context.functions
    matrix = np.array([[1.0, 2.0], [3.0, 4.0]])

    np.testing.assert_allclose(
        functions.get("linsolve")(context, matrix, np.array([5.0, 11.0])),
        np.array([1.0, 2.0]),
    )
    np.testing.assert_allclose(
        functions.get("pinv")(context, matrix),
        np.linalg.pinv(matrix),
    )
    assert functions.get("dot")(context, [1, 2, 3], [4, 5, 6]) == 32
    np.testing.assert_array_equal(
        functions.get("cross")(context, [1, 0, 0], [0, 1, 0]),
        np.array([0, 0, 1]),
    )
    assert functions.get("norm")(context, [3, 4]) == 5
    assert functions.get("trace")(context, matrix) == 5
    assert functions.get("rank")(context, matrix) == 2
    assert functions.get("cond")(context, matrix) == pytest.approx(
        np.linalg.cond(matrix)
    )

    eig = functions.get("eig")(context, matrix)
    np.testing.assert_allclose(
        np.sort(eig["values"]),
        np.sort(np.linalg.eig(matrix)[0]),
    )

    svd = functions.get("svd")(context, matrix)
    assert set(svd.keys()) == {"U", "S", "Vt"}

    np.testing.assert_allclose(
        functions.get("fft")(context, np.array([1, 0, 0, 0])),
        np.array([1, 1, 1, 1]),
    )
    np.testing.assert_allclose(
        functions.get("ifft")(context, np.array([1, 1, 1, 1])),
        np.array([1, 0, 0, 0]),
    )
    np.testing.assert_array_equal(
        functions.get("conv")(context, [1, 2], [3, 4]),
        np.array([3, 10, 8]),
    )
    np.testing.assert_allclose(
        np.sort(functions.get("roots")(context, [1, 0, -1])),
        np.array([-1, 1]),
    )
    assert functions.get("polyval")(context, [1, 0, -1], 3) == 8

    functions.get("rng")(context, 123)
    first = functions.get("rand")(context, 2, 2)
    functions.get("rng")(context, 123)
    second = functions.get("rand")(context, 2, 2)
    np.testing.assert_allclose(first, second)
    assert functions.get("randi")(context, 10) in range(1, 11)


def test_plot_builtins_delegate_to_plot_engine_without_showing_gui():
    context = RuntimeContext()
    context.plot_engine = FakePlotEngine()

    context.functions.get("plot")(context, [1, 2], [3, 4])
    context.functions.get("title")(context, "Title")
    context.functions.get("xlabel")(context, "x")
    context.functions.get("ylabel")(context, "y")
    context.functions.get("grid")(context, True)
    context.functions.get("grid")(context, False)

    assert context.plot_engine.calls == [
        ("plot", [1, 2], [3, 4]),
        ("title", "Title"),
        ("xlabel", "x"),
        ("ylabel", "y"),
        ("grid_on",),
        ("grid_off",),
    ]


def test_plot_engine_displays_nonblocking_and_refreshes(monkeypatch):
    calls = []

    class FakeCanvas:
        def draw_idle(self):
            calls.append(("draw_idle",))

        def flush_events(self):
            calls.append(("flush_events",))

    class FakeFigure:
        canvas = FakeCanvas()

    figure = FakeFigure()

    monkeypatch.setattr(
        "core.plotting.engine.plt.figure",
        lambda: figure,
    )
    monkeypatch.setattr(
        "core.plotting.engine.plt.plot",
        lambda x, y: calls.append(("plot", x, y)),
    )
    monkeypatch.setattr(
        "core.plotting.engine.plt.show",
        lambda block=None: calls.append(("show", block)),
    )
    monkeypatch.setattr(
        "core.plotting.engine.plt.gcf",
        lambda: figure,
    )

    PlotEngine().plot([1, 2], [3, 4])

    assert calls == [
        ("plot", [1, 2], [3, 4]),
        ("show", False),
        ("draw_idle",),
        ("flush_events",),
    ]
