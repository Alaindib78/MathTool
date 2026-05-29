import numpy as np
import pytest

from core.engine import MathToolSession
from core.errors.errors import RuntimeError as MathToolRuntimeError
from core.plotting.engine import PlotEngine
from core.plotting.histogram import compute_histogram_from_arguments
from core.plotting.recording import RecordingPlotEngine


def test_histogram_computes_basic_counts_and_edges():
    histogram = compute_histogram_from_arguments(
        (
            np.array([0, 0.5, 1.5, 2.5, np.nan, np.inf]),
            np.array([0, 1, 2, 3]),
        )
    )

    np.testing.assert_allclose(histogram.RawCounts, [2, 1, 1])
    np.testing.assert_allclose(histogram.Values, [2, 1, 1])
    assert histogram.TotalCount == 6
    assert histogram.Handle.NumBins == 3


def test_histogram_supports_nbins_binwidth_and_normalization():
    data = np.array([0, 1, 2, 3])

    by_count = compute_histogram_from_arguments((data, 2))
    assert by_count.Handle.NumBins == 2

    by_width = compute_histogram_from_arguments(
        (data, "BinWidth", 1, "Normalization", "probability")
    )
    np.testing.assert_allclose(np.sum(by_width.Values), 1.0)
    np.testing.assert_allclose(np.diff(by_width.BinEdges), [1, 1, 1])

    pdf = compute_histogram_from_arguments(
        (data, "BinEdges", [0, 2, 4], "Normalization", "pdf")
    )
    area = np.sum(pdf.Values * np.diff(pdf.BinEdges))
    assert area == pytest.approx(1.0)


def test_histogram_supports_manual_counts():
    histogram = compute_histogram_from_arguments(
        (
            "BinEdges",
            np.array([0, 1, 2, 3]),
            "BinCounts",
            np.array([10, 20, 5]),
            "Normalization",
            "percentage",
        )
    )

    np.testing.assert_allclose(histogram.RawCounts, [10, 20, 5])
    np.testing.assert_allclose(np.sum(histogram.Values), 100.0)


def test_histogram_reports_validation_errors():
    with pytest.raises(MathToolRuntimeError, match="NumBins"):
        compute_histogram_from_arguments((np.arange(10), 0))

    with pytest.raises(MathToolRuntimeError, match="strictly increasing"):
        compute_histogram_from_arguments((np.arange(10), [1, 1, 2]))

    with pytest.raises(MathToolRuntimeError, match="length"):
        compute_histogram_from_arguments(
            ("BinEdges", [0, 1, 2], "BinCounts", [1, 2, 3])
        )

    with pytest.raises(MathToolRuntimeError, match="Normalization"):
        compute_histogram_from_arguments(
            (np.arange(10), "Normalization", "bad")
        )

    with pytest.raises(MathToolRuntimeError, match="unknown option"):
        compute_histogram_from_arguments((np.arange(10), "Foo", 1))


def test_recording_plot_engine_records_histogram_bar_trace():
    engine = RecordingPlotEngine()

    handle = engine.histogram(
        np.array([0, 0.5, 1.5, 2.5]),
        [0, 1, 2, 3],
        "FaceColor",
        "red",
        "EdgeColor",
        "black",
        "FaceAlpha",
        0.4,
        "DisplayName",
        "Data A",
    )

    trace = engine.serialize_plots()[0]["data"][0]
    assert trace["type"] == "bar"
    assert trace["x"] == [0.5, 1.5, 2.5]
    assert trace["y"] == [2.0, 1.0, 1.0]
    assert trace["marker"]["color"] == "red"
    assert trace["marker"]["line"]["color"] == "black"
    assert trace["opacity"] == 0.4
    assert trace["name"] == "Data A"
    assert handle.NumBins == 3


def test_matplotlib_plot_engine_draws_histogram_on_current_axes():
    engine = PlotEngine()
    engine.subplot(2, 1, 1)
    top = engine.ensure_current_axes()
    handle = engine.histogram([0, 0.5, 1.5], [0, 1, 2])

    assert handle.NumBins == 2
    assert len(top.patches) == 2

    engine.subplot(2, 1, 2)
    bottom = engine.ensure_current_axes()
    engine.histogram([2, 2.5, 3.5], [2, 3, 4])

    assert len(bottom.patches) == 2
    assert len(top.patches) == 2
    engine.close("all")


def test_recording_plot_engine_records_stairs_and_horizontal_orientation():
    engine = RecordingPlotEngine()

    engine.histogram(
        [0, 1, 2],
        "BinEdges",
        [0, 1, 2, 3],
        "DisplayStyle",
        "stairs",
        "Orientation",
        "horizontal",
        "LineWidth",
        1.5,
    )

    trace = engine.serialize_plots()[0]["data"][0]
    assert trace["type"] == "scatter"
    assert trace["mode"] == "lines"
    assert trace["line"]["width"] == 1.5
    assert trace["x"] == [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    assert trace["y"] == [0.0, 1.0, 1.0, 2.0, 2.0, 3.0]


def test_session_executes_histogram_and_exposes_handle_properties():
    engine = RecordingPlotEngine()
    session = MathToolSession(plot_engine=engine)

    session.execute(
        """
x = [0 0.5 1.5 2.5];
h = histogram(x, [0 1 2 3], Normalization="probability");
n = h.NumBins;
v = h.Values;
"""
    )

    handle = session.context.get_variable("h")
    np.testing.assert_allclose(handle.Values, [0.5, 0.25, 0.25])
    assert handle.NumBins == 3
    assert session.context.get_variable("n") == 3
    np.testing.assert_allclose(
        session.context.get_variable("v"),
        [0.5, 0.25, 0.25],
    )
    assert session.context.get_variable("h").get_property("NumBins") == 3
    assert engine.serialize_plots()[0]["data"][0]["y"] == [
        0.5,
        0.25,
        0.25,
    ]


def test_histogram_respects_subplot_axis_in_recording_engine():
    engine = RecordingPlotEngine()
    session = MathToolSession(plot_engine=engine)

    session.execute(
        """
subplot(2, 1, 1);
histogram([0 1 2], 2);
subplot(2, 1, 2);
histogram([3 4 5], 2);
"""
    )

    traces = engine.serialize_plots()[0]["data"]
    assert "xaxis" not in traces[0]
    assert traces[1]["xaxis"] == "x2"
    assert traces[1]["yaxis"] == "y2"
