import json

import numpy as np

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
