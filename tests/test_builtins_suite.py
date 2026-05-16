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

    np.testing.assert_allclose(sin(context, values), np.array([0, 1]))
    np.testing.assert_array_equal(sqrt(context, np.array([4, 9])), np.array([2, 3]))
    np.testing.assert_array_equal(ones(context, 3), np.array([1, 1, 1]))
    assert length(context, values) == 2


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
