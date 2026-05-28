import numpy as np

from core.serialization import json_leaf
from core.plotting.plot_parser import parse_plot_arguments


class RecordingPlotEngine:
    def __init__(self):
        self.plots = []
        self.current_plot = None
        self.next_id = 1
        self.hold_enabled = False

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

    def plot(self, *arguments):
        series = parse_plot_arguments(arguments)

        if self.current_plot is None:
            self.figure()

        if not self.hold_enabled:
            self.current_plot["data"] = []

        for item in series:
            self.current_plot["data"].append(
                self.trace_for_series(item)
            )

        return self.current_plot["data"][-len(series):]

    def trace_for_series(self, series):
        trace = {
            "type": "scatter",
            "mode": self.mode_for_series(series),
            "x": self.line_values(series.x),
            "y": self.line_values(series.y),
        }

        line = {}
        marker = {}

        properties = series.properties

        if "Color" in properties:
            line["color"] = self.color_value(properties["Color"])
            marker["color"] = self.color_value(properties["Color"])

        if "LineStyle" in properties:
            line["dash"] = self.dash_value(
                properties["LineStyle"]
            )

        if "LineWidth" in properties:
            line["width"] = properties["LineWidth"]

        if "Marker" in properties:
            marker["symbol"] = self.marker_value(
                properties["Marker"]
            )

        if "MarkerSize" in properties:
            marker["size"] = properties["MarkerSize"]

        if "MarkerFaceColor" in properties:
            marker["color"] = self.color_value(
                properties["MarkerFaceColor"]
            )

        if "MarkerEdgeColor" in properties:
            marker["line"] = {
                "color": self.color_value(
                    properties["MarkerEdgeColor"]
                )
            }

        if "MarkerIndices" in properties:
            trace["marker_indices"] = properties[
                "MarkerIndices"
            ]

        if line:
            trace["line"] = line

        if marker:
            trace["marker"] = marker

        return trace

    def mode_for_series(self, series):
        line_style = series.properties.get("LineStyle")
        marker = series.properties.get("Marker")

        has_line = line_style != "none"
        has_marker = marker is not None and marker != "none"

        if has_line and has_marker:
            return "lines+markers"

        if has_marker:
            return "markers"

        return "lines"

    def dash_value(self, line_style):
        return {
            "-": "solid",
            "--": "dash",
            ":": "dot",
            "-.": "dashdot",
            "none": "none",
        }.get(line_style, "solid")

    def marker_value(self, marker):
        return {
            "o": "circle",
            "+": "cross",
            "*": "star",
            ".": "circle",
            "x": "x",
            "s": "square",
            "d": "diamond",
            "^": "triangle-up",
            "v": "triangle-down",
            ">": "triangle-right",
            "<": "triangle-left",
            "p": "pentagon",
            "h": "hexagon",
        }.get(marker, marker)

    def color_value(self, color):
        if isinstance(color, tuple):
            red, green, blue = color
            return f"rgb({red * 255:.0f},{green * 255:.0f},{blue * 255:.0f})"

        return color

    def hold(self, mode=None):
        if mode is None:
            self.hold_enabled = not self.hold_enabled
            return self.hold_enabled

        if isinstance(mode, str):
            lowered = mode.lower()

            if lowered == "on":
                self.hold_enabled = True
                return self.hold_enabled

            if lowered == "off":
                self.hold_enabled = False
                return self.hold_enabled

        self.hold_enabled = bool(mode)
        return self.hold_enabled

    def bode(self, frequency, magnitude_db, phase_deg):
        self.figure()
        self.plot(frequency, magnitude_db)
        self.title("Bode Diagram - Magnitude")
        self.xlabel("Frequency (rad/s)")
        self.ylabel("Magnitude (dB)")
        self.grid_on()
        self.current_plot["layout"]["xaxis"]["type"] = "log"

        self.figure()
        self.plot(frequency, phase_deg)
        self.title("Bode Diagram - Phase")
        self.xlabel("Frequency (rad/s)")
        self.ylabel("Phase (deg)")
        self.grid_on()
        self.current_plot["layout"]["xaxis"]["type"] = "log"

    def nyquist(self, real_values, imag_values):
        self.figure()
        self.plot(real_values, imag_values)
        self.title("Nyquist Diagram")
        self.xlabel("Real")
        self.ylabel("Imaginary")
        self.grid_on()

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
