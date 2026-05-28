import numpy as np

from core.errors.errors import RuntimeError as MathToolRuntimeError
from core.serialization import json_leaf
from core.plotting.axis_manager import apply_recording_axis
from core.plotting.legend_manager import parse_legend_arguments
from core.plotting.plot_parser import parse_plot_arguments
from core.plotting.reference_lines import (
    label_for_index,
    parse_reference_line_arguments,
)
from core.plotting.subplot_manager import parse_subplot_arguments
from core.plotting.tick_manager import (
    tick_labels_from_arguments,
    tick_values_from_argument,
)


class RecordingPlotEngine:
    def __init__(self):
        self.plots = []
        self.current_plot = None
        self.next_id = 1
        self.hold_enabled = False
        self.current_axis_by_plot = {}

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
        self.current_axis_by_plot[figure_id] = 1

    def plot(self, *arguments):
        series = parse_plot_arguments(arguments)

        if self.current_plot is None:
            self.figure()

        if not self.hold_enabled:
            self.clear_current_axis_traces()

        for item in series:
            trace = self.trace_for_series(item)
            self.apply_axis_reference(trace)
            self.current_plot["data"].append(trace)

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

        if "DisplayName" in properties:
            trace["name"] = properties["DisplayName"]
            trace["showlegend"] = True

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
        self.current_axis_by_plot.pop(figure_id, None)

    def find_plot(self, figure_id):
        for plot in self.plots:
            if plot["id"] == figure_id:
                return plot

        return None

    def title(self, text):
        plot_spec = self.ensure_current_plot()

        if self.current_axis_number() == 1:
            plot_spec["layout"]["title"]["text"] = str(text)
        else:
            plot_spec["layout"].setdefault("annotations", []).append(
                {
                    "text": str(text),
                    "xref": self.axis_reference("x", domain=True),
                    "yref": self.axis_reference("y", domain=True),
                    "x": 0.5,
                    "y": 1.0,
                    "showarrow": False,
                }
            )

    def xlabel(self, text):
        self.current_axis_layout("x")["title"]["text"] = str(text)

    def ylabel(self, text):
        self.current_axis_layout("y")["title"]["text"] = str(text)

    def grid_on(self):
        self.set_grid(True)

    def grid_off(self):
        self.set_grid(False)

    def set_grid(self, enabled):
        self.current_axis_layout("x")["showgrid"] = enabled
        self.current_axis_layout("y")["showgrid"] = enabled

    def subplot(self, *arguments):
        plot_spec = self.ensure_current_plot()
        spec = parse_subplot_arguments(arguments)

        if spec["kind"] == "position":
            axis_number = self.next_axis_number(plot_spec)
            self.current_axis_by_plot[plot_spec["id"]] = axis_number
            self.apply_axis_domains(
                axis_number,
                spec["position"],
                plot_spec,
            )
            return None

        if len(spec["indices"]) != 1:
            raise MathToolRuntimeError(
                "subplot: vector p is not supported by recording plots"
            )

        axis_number = spec["indices"][0]
        self.current_axis_by_plot[plot_spec["id"]] = axis_number
        self.apply_subplot_domains(
            spec["rows"],
            spec["columns"],
            axis_number,
            plot_spec,
        )
        return None

    def xticks(self, *arguments):
        return self.ticks("x", *arguments)

    def yticks(self, *arguments):
        return self.ticks("y", *arguments)

    def ticks(self, dimension, *arguments):
        axis = self.current_axis_layout(dimension)
        function_name = f"{dimension}ticks"

        if not arguments:
            return np.asarray(axis.get("tickvals", []), dtype=float)

        if len(arguments) == 1 and isinstance(arguments[0], str):
            option = arguments[0].lower()

            if option == "mode":
                return axis.get("tickmode", "auto")

            if option in {"auto", "manual"}:
                axis["tickmode"] = option
                if option == "auto":
                    axis.pop("tickvals", None)
                return None

        if len(arguments) != 1:
            raise MathToolRuntimeError(
                f"{function_name}: expected zero or one argument"
            )

        values = tick_values_from_argument(arguments[0], function_name)
        axis["tickvals"] = self.line_values(values)
        axis["tickmode"] = "manual"
        return None

    def xticklabels(self, *arguments):
        return self.ticklabels("x", *arguments)

    def yticklabels(self, *arguments):
        return self.ticklabels("y", *arguments)

    def ticklabels(self, dimension, *arguments):
        axis = self.current_axis_layout(dimension)
        function_name = f"{dimension}ticklabels"

        if not arguments:
            return axis.get("ticktext", [])

        if len(arguments) == 1 and isinstance(arguments[0], str):
            option = arguments[0].lower()

            if option == "mode":
                return axis.get("ticklabelmode", "auto")

            if option in {"auto", "manual"}:
                axis["ticklabelmode"] = option
                if option == "auto":
                    axis.pop("ticktext", None)
                return None

        labels = tick_labels_from_arguments(
            arguments,
            function_name,
            len(axis.get("tickvals", [])),
        )
        axis["ticktext"] = labels
        axis["ticklabelmode"] = "manual"
        axis["tickmode"] = "manual"
        return None

    def xline(self, *arguments):
        return self.reference_line("x", *arguments)

    def yline(self, *arguments):
        return self.reference_line("y", *arguments)

    def reference_line(self, dimension, *arguments):
        plot_spec = self.ensure_current_plot()
        coordinates, properties, labels = parse_reference_line_arguments(
            arguments,
            f"{dimension}line",
        )
        traces = []

        for index, coordinate in enumerate(coordinates):
            trace = {
                "type": "scatter",
                "mode": "lines",
                "showlegend": False,
            }

            if dimension == "x":
                trace["x"] = [float(coordinate), float(coordinate)]
                trace["y"] = [0, 1]
                trace["yref"] = self.axis_reference("y", domain=True)
            else:
                trace["x"] = [0, 1]
                trace["y"] = [float(coordinate), float(coordinate)]
                trace["xref"] = self.axis_reference("x", domain=True)

            self.apply_axis_reference(trace)
            line = {}

            if "Color" in properties:
                line["color"] = self.color_value(properties["Color"])

            if "LineWidth" in properties:
                line["width"] = properties["LineWidth"]

            if "LineStyle" in properties:
                line["dash"] = self.dash_value(properties["LineStyle"])

            if line:
                trace["line"] = line

            label = label_for_index(labels, index)
            if label is not None:
                trace["name"] = label

            if "DisplayName" in properties:
                trace["name"] = properties["DisplayName"]

            traces.append(trace)
            plot_spec["data"].append(trace)

        return traces[0] if len(traces) == 1 else traces

    def legend(self, *arguments):
        plot_spec = self.ensure_current_plot()
        command, labels, properties = parse_legend_arguments(arguments)

        if command == "off":
            plot_spec["layout"]["showlegend"] = False
            return None

        if command in {"show", "create"}:
            plot_spec["layout"]["showlegend"] = True

        if command == "hide":
            plot_spec["layout"]["showlegend"] = False
            return None

        if labels:
            visible_traces = [
                trace
                for trace in plot_spec["data"]
                if trace.get("x") or trace.get("y")
            ]

            for trace, label in zip(visible_traces, labels):
                trace["name"] = label
                trace["showlegend"] = True

        if "Location" in properties:
            plot_spec["layout"]["legend"] = {
                "location": properties["Location"],
            }

        if properties.get("Orientation") == "horizontal":
            plot_spec.setdefault("layout", {}).setdefault(
                "legend",
                {},
            )["orientation"] = "h"

        return None

    def axis(self, *arguments):
        return apply_recording_axis(self, *arguments)

    def serialize_plots(self):
        return list(self.plots)

    def clear(self):
        self.plots.clear()
        self.current_plot = None
        self.current_axis_by_plot.clear()

    def ensure_current_plot(self):
        if self.current_plot is None:
            self.figure()

        return self.current_plot

    def current_axis_number(self):
        plot_spec = self.ensure_current_plot()
        return self.current_axis_by_plot.get(plot_spec["id"], 1)

    def current_axis_layout(self, dimension):
        plot_spec = self.ensure_current_plot()
        key = self.axis_layout_key(
            dimension,
            self.current_axis_number(),
        )
        layout = plot_spec["layout"].setdefault(
            key,
            {
                "title": {
                    "text": "",
                },
                "showgrid": False,
            },
        )
        layout.setdefault("title", {"text": ""})
        return layout

    def axis_layout_key(self, dimension, axis_number):
        if axis_number == 1:
            return f"{dimension}axis"

        return f"{dimension}axis{axis_number}"

    def axis_reference(self, dimension, domain=False):
        axis_number = self.current_axis_number()

        if domain:
            suffix = "" if axis_number == 1 else str(axis_number)
            return f"{dimension}{suffix} domain"

        return dimension if axis_number == 1 else f"{dimension}{axis_number}"

    def apply_axis_reference(self, trace):
        axis_number = self.current_axis_number()

        if axis_number != 1:
            trace["xaxis"] = f"x{axis_number}"
            trace["yaxis"] = f"y{axis_number}"

    def clear_current_axis_traces(self):
        axis_number = self.current_axis_number()

        if axis_number == 1:
            self.current_plot["data"] = [
                trace
                for trace in self.current_plot["data"]
                if trace.get("xaxis") or trace.get("yaxis")
            ]
            return

        xref = f"x{axis_number}"
        yref = f"y{axis_number}"
        self.current_plot["data"] = [
            trace
            for trace in self.current_plot["data"]
            if (
                trace.get("xaxis") != xref
                or trace.get("yaxis") != yref
            )
            and not self.is_empty_default_trace(trace)
        ]

    def is_empty_default_trace(self, trace):
        return (
            not trace.get("x")
            and not trace.get("y")
            and "xaxis" not in trace
            and "yaxis" not in trace
        )

    def apply_subplot_domains(
        self,
        rows,
        columns,
        axis_number,
        plot_spec,
    ):
        row = (axis_number - 1) // columns
        column = (axis_number - 1) % columns
        x0 = column / columns
        x1 = (column + 1) / columns
        y0 = 1 - ((row + 1) / rows)
        y1 = 1 - (row / rows)
        self.apply_axis_domains(
            axis_number,
            [x0, y0, x1 - x0, y1 - y0],
            plot_spec,
        )

    def apply_axis_domains(self, axis_number, position, plot_spec):
        left, bottom, width, height = position
        plot_spec["layout"][self.axis_layout_key("x", axis_number)] = {
            "domain": [left, left + width],
            "title": {"text": ""},
            "showgrid": False,
        }
        plot_spec["layout"][self.axis_layout_key("y", axis_number)] = {
            "domain": [bottom, bottom + height],
            "title": {"text": ""},
            "showgrid": False,
        }

    def next_axis_number(self, plot_spec):
        existing = [
            1
            for key in plot_spec["layout"]
            if key.startswith("xaxis")
        ]
        return len(existing) + 1

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
