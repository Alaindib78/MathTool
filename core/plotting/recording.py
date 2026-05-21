import numpy as np

from core.serialization import json_leaf


class RecordingPlotEngine:
    def __init__(self):
        self.plots = []
        self.current_plot = None
        self.next_id = 1

    def plot(self, x, y):
        plot_spec = {
            "id": self.next_id,
            "type": "plotly",
            "data": [
                {
                    "type": "scatter",
                    "mode": "lines",
                    "x": self.line_values(x),
                    "y": self.line_values(y),
                },
            ],
            "layout": {
                "title": {
                    "text": "",
                },
                "xaxis": {
                    "title": {
                        "text": "",
                    },
                    "showgrid": False,
                },
                "yaxis": {
                    "title": {
                        "text": "",
                    },
                    "showgrid": False,
                },
            },
        }

        self.next_id += 1
        self.plots.append(plot_spec)
        self.current_plot = plot_spec

    def title(self, text):
        plot_spec = self.ensure_current_plot()

        plot_spec["layout"]["title"]["text"] = str(text)

    def xlabel(self, text):
        plot_spec = self.ensure_current_plot()

        plot_spec["layout"]["xaxis"]["title"]["text"] = (
            str(text)
        )

    def ylabel(self, text):
        plot_spec = self.ensure_current_plot()

        plot_spec["layout"]["yaxis"]["title"]["text"] = (
            str(text)
        )

    def grid_on(self):
        self.set_grid(True)

    def grid_off(self):
        self.set_grid(False)

    def set_grid(self, enabled):
        plot_spec = self.ensure_current_plot()

        plot_spec["layout"]["xaxis"]["showgrid"] = enabled
        plot_spec["layout"]["yaxis"]["showgrid"] = enabled

    def serialize_plots(self):
        return list(self.plots)

    def clear(self):
        self.plots.clear()
        self.current_plot = None

    def ensure_current_plot(self):
        if self.current_plot is None:
            self.plot([], [])

        return self.current_plot

    def line_values(self, value):
        array = np.asarray(value)

        if array.ndim == 0:
            return [
                json_leaf(array.item())
            ]

        if array.ndim == 1:
            return json_leaf(array.tolist())

        if 1 in array.shape:
            return json_leaf(
                array.reshape(-1).tolist()
            )

        return json_leaf(array.tolist())
