import json

import numpy as np
import pytest

from core.engine import MathToolSession
from core.errors.errors import RuntimeError as MathToolRuntimeError
from core.plotting.recording import RecordingPlotEngine


def test_recording_plot_engine_builds_plotly_style_spec():
    engine = RecordingPlotEngine()

    engine.plot(
        np.array([1, 2, 3]),
        np.array([4, 5, 6]),
    )
    engine.title("Line")
    engine.xlabel("x")
    engine.ylabel("y")
    engine.grid_on()

    plots = engine.serialize_plots()

    assert plots == [
        {
            "id": 1,
            "type": "plotly",
            "data": [
                {
                    "type": "scatter",
                    "mode": "lines",
                    "x": [1, 2, 3],
                    "y": [4, 5, 6],
                },
            ],
            "layout": {
                "title": {
                    "text": "Line",
                },
                "xaxis": {
                    "title": {
                        "text": "x",
                    },
                    "showgrid": True,
                },
                "yaxis": {
                    "title": {
                        "text": "y",
                    },
                    "showgrid": True,
                },
            },
        },
    ]

    json.dumps(plots, allow_nan=False)


def test_recording_plot_engine_flattens_column_vectors():
    engine = RecordingPlotEngine()

    engine.plot(
        np.array([[1], [2], [3]]),
        np.array([[4], [5], [6]]),
    )

    trace = engine.serialize_plots()[0]["data"][0]

    assert trace["x"] == [1, 2, 3]
    assert trace["y"] == [4, 5, 6]


def test_recording_plot_engine_supports_implicit_x_and_matrix_columns():
    engine = RecordingPlotEngine()

    engine.plot(np.array([4, 5, 6]))

    trace = engine.serialize_plots()[0]["data"][0]
    assert trace["x"] == [1, 2, 3]
    assert trace["y"] == [4, 5, 6]

    engine.plot(
        np.array(
            [
                [1, 3, 5],
                [2, 4, 6],
                [3, 5, 7],
                [4, 6, 8],
            ]
        )
    )

    traces = engine.serialize_plots()[0]["data"]

    assert len(traces) == 3
    assert traces[0]["x"] == [1, 2, 3, 4]
    assert traces[0]["y"] == [1, 2, 3, 4]
    assert traces[1]["y"] == [3, 4, 5, 6]
    assert traces[2]["y"] == [5, 6, 7, 8]


def test_recording_plot_engine_supports_multiple_pairs_and_line_specs():
    engine = RecordingPlotEngine()
    x = np.array([1, 2, 3])

    engine.plot(
        x,
        np.array([1, 4, 9]),
        "r--",
        x,
        np.array([1, 8, 27]),
        "bo",
        x,
        np.array([1, 16, 81]),
        "g-*",
    )

    traces = engine.serialize_plots()[0]["data"]

    assert len(traces) == 3
    assert traces[0]["line"]["color"] == "r"
    assert traces[0]["line"]["dash"] == "dash"
    assert traces[1]["mode"] == "markers"
    assert traces[1]["marker"]["symbol"] == "circle"
    assert traces[1]["marker"]["color"] == "b"
    assert traces[2]["mode"] == "lines+markers"
    assert traces[2]["line"]["color"] == "g"
    assert traces[2]["marker"]["symbol"] == "star"


def test_recording_plot_engine_supports_name_value_properties():
    engine = RecordingPlotEngine()

    engine.plot(
        [1, 2, 3],
        [4, 5, 6],
        "--gs",
        "LineWidth",
        2,
        "MarkerSize",
        10,
        "MarkerEdgeColor",
        "b",
        "MarkerFaceColor",
        [0.5, 0.5, 0.5],
    )

    trace = engine.serialize_plots()[0]["data"][0]

    assert trace["mode"] == "lines+markers"
    assert trace["line"]["dash"] == "dash"
    assert trace["line"]["width"] == 2.0
    assert trace["marker"]["symbol"] == "square"
    assert trace["marker"]["size"] == 10.0
    assert trace["marker"]["line"]["color"] == "b"
    assert trace["marker"]["color"] == "rgb(128,128,128)"

    engine.plot(
        [1, 2, 3],
        [4, 5, 6],
        "Color",
        [0, 0.7, 0.9],
    )

    trace = engine.serialize_plots()[0]["data"][0]

    assert trace["line"]["color"] == "rgb(0,178,230)"


def test_recording_plot_engine_supports_hold_state():
    engine = RecordingPlotEngine()

    engine.plot([1, 2], [3, 4])
    engine.hold("on")
    engine.plot([1, 2], [5, 6])

    assert len(engine.serialize_plots()[0]["data"]) == 2

    engine.hold("off")
    engine.plot([1, 2], [7, 8])

    traces = engine.serialize_plots()[0]["data"]

    assert len(traces) == 1
    assert traces[0]["y"] == [7, 8]


def test_recording_plot_engine_reports_plot_argument_errors():
    engine = RecordingPlotEngine()

    with pytest.raises(MathToolRuntimeError, match="same length"):
        engine.plot([1, 2], [3, 4, 5])

    with pytest.raises(MathToolRuntimeError, match="Invalid LineSpec"):
        engine.plot([1, 2], [3, 4], "rq--")

    with pytest.raises(MathToolRuntimeError, match="Unknown property"):
        engine.plot([1, 2], [3, 4], "Foo", 1)


def test_session_supports_hold_and_grid_command_syntax():
    engine = RecordingPlotEngine()
    session = MathToolSession(plot_engine=engine)

    session.execute(
        """
plot([1 2], [3 4]);
hold on;
plot([1 2], [5 6]);
grid on;
"""
    )

    plot = engine.serialize_plots()[0]

    assert len(plot["data"]) == 2
    assert plot["layout"]["xaxis"]["showgrid"] is True
    assert plot["layout"]["yaxis"]["showgrid"] is True

    session.execute(
        """
hold off;
plot([1 2], [7 8]);
grid off;
"""
    )

    plot = engine.serialize_plots()[0]

    assert len(plot["data"]) == 1
    assert plot["data"][0]["y"] == [7, 8]
    assert plot["layout"]["xaxis"]["showgrid"] is False


def test_recording_plot_engine_records_bode_and_nyquist_specs():
    engine = RecordingPlotEngine()

    engine.bode(
        np.array([0.1, 1.0]),
        np.array([-0.04321374, -3.01029996]),
        np.array([-5.71059314, -45.0]),
    )
    engine.nyquist(
        np.array([1.0, 0.5, 0.5, 1.0]),
        np.array([0.0, -0.5, 0.5, 0.0]),
    )

    plots = engine.serialize_plots()

    assert [
        plot["layout"]["title"]["text"]
        for plot in plots
    ] == [
        "Bode Diagram - Magnitude",
        "Bode Diagram - Phase",
        "Nyquist Diagram",
    ]
    assert plots[0]["layout"]["xaxis"]["type"] == "log"
    assert plots[1]["layout"]["xaxis"]["type"] == "log"
    assert plots[2]["data"][0]["x"] == [1.0, 0.5, 0.5, 1.0]

    json.dumps(plots, allow_nan=False)


def test_recording_plot_engine_creates_empty_current_plot_for_labels():
    engine = RecordingPlotEngine()

    engine.title("Untitled")

    plots = engine.serialize_plots()

    assert plots[0]["data"][0]["x"] == []
    assert plots[0]["layout"]["title"]["text"] == "Untitled"


def test_recording_plot_engine_supports_figure_and_close():
    engine = RecordingPlotEngine()

    engine.figure(2)
    engine.plot([1, 2], [3, 4])
    engine.figure(5)
    engine.plot([5, 6], [7, 8])
    engine.figure(2)
    engine.title("two")

    plots = engine.serialize_plots()

    assert [
        plot["id"]
        for plot in plots
    ] == [2, 5]
    assert plots[0]["layout"]["title"]["text"] == "two"
    assert plots[0]["data"][0]["x"] == [1, 2]
    assert plots[1]["data"][0]["x"] == [5, 6]

    engine.close(2)

    assert [
        plot["id"]
        for plot in engine.serialize_plots()
    ] == [5]

    engine.close()

    assert engine.serialize_plots() == []


def test_recording_plot_engine_supports_close_all():
    engine = RecordingPlotEngine()

    engine.figure(1)
    engine.figure(2)
    engine.close("all")

    assert engine.serialize_plots() == []
