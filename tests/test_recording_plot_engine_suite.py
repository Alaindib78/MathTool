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
