import numpy as np

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
    np.testing.assert_array_equal(ones(context, 3), np.array([1, 1, 1]))
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
