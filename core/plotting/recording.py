import numpy as np

from core.serialization import json_leaf


class RecordingPlotEngine:
    def __init__(self):
        self.plots = []
        self.current_plot = None
        self.next_id = 1

    def figure(self, number=None):
        figure_id = (
            self.next_id
            if number is None
            else int(number)
        )

        existing_plot = self.find_plot(figure_id)

        if existing_plot is not None:
            self.current_plot = existing_plot
            return

        plot_spec = self.empty_plot(figure_id)

        self.next_id = max(
            self.next_id,
            figure_id + 1,
        )
        self.plots.append(plot_spec)
        self.current_plot = plot_spec

    def plot(self, x, y):
        if self.current_plot is None:
            self.figure()

        self.current_plot["data"] = [
            {
                "type": "scatter",
                "mode": "lines",
                "x": self.line_values(x),
                "y": self.line_values(y),
            },
        ]

    def close(self, target=None):
        if target == "all":
            self.clear()
            return

        if target is None:
            if self.current_plot is not None:
                self.remove_plot(
                    self.current_plot["id"]
                )

            return

        self.remove_plot(int(target))

    def empty_plot(self, figure_id):
        return {
            "id": figure_id,
            "type": "plotly",
            "data": [
                {
                    "type": "scatter",
                    "mode": "lines",
                    "x": [],
                    "y": [],
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

    def remove_plot(self, figure_id):
        self.plots = [
            plot
            for plot in self.plots
            if plot["id"] != figure_id
        ]

        if (
            self.current_plot is not None
            and self.current_plot["id"] == figure_id
        ):
            self.current_plot = (
                self.plots[-1]
                if self.plots
                else None
            )

    def find_plot(self, figure_id):
        for plot in self.plots:
            if plot["id"] == figure_id:
                return plot

        return None

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
            self.figure()

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
