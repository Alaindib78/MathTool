import numpy as np
import pytest

from core.plotting.engine import PlotEngine
from core.plotting.recording import RecordingPlotEngine
from core.runtime.context import RuntimeContext


class FakePlotEngine:
    def __init__(self):
        self.calls = []

    def plot(self, *arguments):
        self.calls.append(("plot", *arguments))

    def histogram(self, *arguments):
        self.calls.append(("histogram", *arguments))

    def figure(self, number=None):
        self.calls.append(("figure", number))

    def close(self, target=None):
        self.calls.append(("close", target))

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

    def hold(self, mode=None):
        self.calls.append(("hold", mode))

    def xticks(self, *arguments):
        self.calls.append(("xticks", *arguments))

    def xticklabels(self, *arguments):
        self.calls.append(("xticklabels", *arguments))

    def yticks(self, *arguments):
        self.calls.append(("yticks", *arguments))

    def yticklabels(self, *arguments):
        self.calls.append(("yticklabels", *arguments))

    def xline(self, *arguments):
        self.calls.append(("xline", *arguments))

    def yline(self, *arguments):
        self.calls.append(("yline", *arguments))

    def legend(self, *arguments):
        self.calls.append(("legend", *arguments))

    def subplot(self, *arguments):
        self.calls.append(("subplot", *arguments))

    def axis(self, *arguments):
        self.calls.append(("axis", *arguments))


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


def test_integer_conversion_and_bitwise_builtins():
    context = RuntimeContext()
    functions = context.functions

    assert functions.get("dec2hex")(context, 255) == "FF"
    assert functions.get("dec2bin")(context, 16) == "10000"
    assert functions.get("hex2dec")(context, "FF") == 255
    assert functions.get("bin2dec")(context, "1010") == 10

    assert functions.get("dec2hex")(context, np.array([15, 16])) == [
        "F",
        "10",
    ]
    assert functions.get("hex2dec")(context, np.array(["F", "10"])) == [
        15,
        16,
    ]

    assert functions.get("bitand")(context, 0b1100, 0b1010) == 0b1000
    assert functions.get("bitor")(context, 0b1100, 0b1010) == 0b1110
    assert functions.get("bitxor")(context, 0b1100, 0b1010) == 0b0110
    assert functions.get("bitshift")(context, 0b0011, 2) == 0b1100
    assert functions.get("bitshift")(context, 0b1100, -2) == 0b0011
    assert functions.get("bitget")(context, 0b1010, 2) == 1
    assert functions.get("bitset")(context, 0b1000, 2, True) == 0b1010
    assert functions.get("bitset")(context, 0b1010, 2, False) == 0b1000
    assert functions.get("bitset")(
        context,
        np.uint8(0b10010110),
        5,
        False,
    ) == np.uint8(0b10000110)


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
    context.functions.get("histogram")(context, [1, 2, 2, 3])
    context.functions.get("title")(context, "Title")
    context.functions.get("xlabel")(context, "x")
    context.functions.get("ylabel")(context, "y")
    context.functions.get("grid")(context, True)
    context.functions.get("grid")(context, False)
    context.functions.get("hold")(context, "on")
    context.functions.get("xticks")(context, [0, 1])
    context.functions.get("xticklabels")(context, "zero", "one")
    context.functions.get("yticks")(context, [-1, 1])
    context.functions.get("yticklabels")(context, ["low", "high"])
    context.functions.get("xline")(context, 0, "--r", "zero")
    context.functions.get("yline")(context, 1, ":k")
    context.functions.get("legend")(context, "a", "b")
    context.functions.get("subplot")(context, 2, 1, 1)
    context.functions.get("axis")(context, [0, 1, -1, 1])
    context.functions.get("figure")(context)
    context.functions.get("figure")(context, 2)
    context.functions.get("close")(context)
    context.functions.get("close")(context, 2)
    context.functions.get("close")(context, "ALL")

    assert context.plot_engine.calls == [
        ("plot", [1, 2], [3, 4]),
        ("histogram", [1, 2, 2, 3]),
        ("title", "Title"),
        ("xlabel", "x"),
        ("ylabel", "y"),
        ("grid_on",),
        ("grid_off",),
        ("hold", "on"),
        ("xticks", [0, 1]),
        ("xticklabels", "zero", "one"),
        ("yticks", [-1, 1]),
        ("yticklabels", ["low", "high"]),
        ("xline", 0, "--r", "zero"),
        ("yline", 1, ":k"),
        ("legend", "a", "b"),
        ("subplot", 2, 1, 1),
        ("axis", [0, 1, -1, 1]),
        ("figure", None),
        ("figure", 2),
        ("close", None),
        ("close", 2),
        ("close", "all"),
    ]


def test_bode_and_nyquist_builtins_record_control_plots():
    context = RuntimeContext()
    context.plot_engine = RecordingPlotEngine()
    functions = context.functions
    frequency = np.array([0.1, 1.0, 10.0])

    functions.get("bode")(
        context,
        np.array([1.0]),
        np.array([1.0, 1.0]),
        frequency,
    )
    functions.get("nyquist")(
        context,
        np.array([1.0]),
        np.array([1.0, 1.0]),
        np.array([0.0, 1.0]),
    )

    plots = context.plot_engine.serialize_plots()

    assert [
        plot["layout"]["title"]["text"]
        for plot in plots
    ] == [
        "Bode Diagram - Magnitude",
        "Bode Diagram - Phase",
        "Nyquist Diagram",
    ]
    np.testing.assert_allclose(
        plots[0]["data"][0]["y"],
        np.array([-0.04321374, -3.01029996, -20.04321374]),
    )
    np.testing.assert_allclose(
        plots[1]["data"][0]["y"],
        np.array([-5.71059314, -45.0, -84.28940686]),
    )
    assert plots[0]["layout"]["xaxis"]["type"] == "log"
    assert plots[2]["data"][0]["x"] == [1.0, 0.5, 0.5, 1.0]
    assert plots[2]["data"][0]["y"] == [0.0, -0.5, 0.5, -0.0]


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


def test_plot_engine_supports_figure_and_close(monkeypatch):
    calls = []

    class FakeFigure:
        def __init__(self, number):
            self.number = number
            self.canvas = None

    def fake_figure(number=None):
        calls.append(("figure", number))
        return FakeFigure(number or 1)

    monkeypatch.setattr(
        "core.plotting.engine.plt.figure",
        fake_figure,
    )
    monkeypatch.setattr(
        "core.plotting.engine.plt.show",
        lambda block=None: calls.append(("show", block)),
    )
    monkeypatch.setattr(
        "core.plotting.engine.plt.gcf",
        lambda: FakeFigure(1),
    )
    monkeypatch.setattr(
        "core.plotting.engine.plt.close",
        lambda target=None: calls.append(("close", target)),
    )

    engine = PlotEngine()

    engine.figure()
    engine.figure(2)
    engine.close()
    engine.figure(3)
    engine.close(3)
    engine.close("all")

    assert calls == [
        ("figure", None),
        ("show", False),
        ("figure", 2),
        ("show", False),
        ("close", None),
        ("figure", 3),
        ("show", False),
        ("close", 3),
        ("close", "all"),
    ]


def test_plot_engine_targets_current_subplot_axes(monkeypatch):
    import matplotlib.pyplot as plt

    monkeypatch.setattr(PlotEngine, "show", lambda self: None)
    monkeypatch.setattr(PlotEngine, "refresh", lambda self: None)
    plt.close("all")

    engine = PlotEngine()
    engine.subplot(2, 1, 1)
    engine.plot([0, 1], [0, 1])
    engine.title("Top")
    engine.yline(0)
    engine.xticks([0, 0.5, 1])
    top_axis = engine.current_axes_by_figure[
        engine.figure_number(engine.current_figure)
    ]

    engine.subplot(2, 1, 2)
    engine.plot([0, 1], [1, 0])
    engine.title("Bottom")
    engine.xline(0.5)
    bottom_axis = engine.current_axes_by_figure[
        engine.figure_number(engine.current_figure)
    ]

    assert top_axis is not bottom_axis
    assert top_axis.get_title() == "Top"
    assert bottom_axis.get_title() == "Bottom"
    assert len(top_axis.lines) == 2
    assert len(bottom_axis.lines) == 2
    np.testing.assert_allclose(top_axis.get_xticks(), [0, 0.5, 1])

    plt.close("all")


def test_plot_engine_supports_axis_limits_styles_and_query(monkeypatch):
    import matplotlib.pyplot as plt

    monkeypatch.setattr(PlotEngine, "show", lambda self: None)
    monkeypatch.setattr(PlotEngine, "refresh", lambda self: None)
    plt.close("all")

    engine = PlotEngine()
    engine.plot([0, 1, 2], [-1, 0, 1])
    engine.axis([0, 2, -2, 2])

    np.testing.assert_allclose(engine.axis(), [0, 2, -2, 2])

    axis = engine.ensure_current_axes()
    engine.axis("ij")
    assert axis.yaxis_inverted()
    engine.axis("xy")
    assert not axis.yaxis_inverted()
    engine.axis("equal")
    assert axis.get_aspect() == 1.0
    engine.axis("off")
    assert not axis.axison
    engine.axis("on")
    assert axis.axison

    plt.close("all")
