import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba

from core.errors.errors import RuntimeError as MathToolRuntimeError
from core.plotting.axis_manager import apply_matplotlib_axis
from core.plotting.histogram import compute_histogram_from_arguments
from core.plotting.legend_manager import (
    apply_legend_text_options,
    legend_kwargs,
    parse_legend_arguments,
)
from core.plotting.line_spec import matplotlib_kwargs
from core.plotting.plot_parser import parse_plot_arguments
from core.plotting.reference_lines import (
    label_for_index,
    parse_reference_line_arguments,
    reference_line_kwargs,
    text_alignment,
    text_rotation,
)
from core.plotting.subplot_manager import (
    parse_subplot_arguments,
    select_subplot_axis,
)
from core.plotting.tick_manager import (
    get_tick_label_mode,
    get_tick_mode,
    get_ticklabels,
    get_ticks,
    set_tick_label_mode,
    set_tick_mode,
    set_ticklabels,
    set_ticks,
    tick_labels_from_arguments,
    tick_values_from_argument,
)


class PlotEngine:
    def __init__(self):
        self.current_figure = None
        self.current_axes_by_figure = {}
        self.subplot_axes_by_figure = {}
        self.hold_enabled = False

    def figure(self, number=None):
        self.current_figure = plt.figure(
            None if number is None else int(number)
        )
        self.restore_current_axes()

        self.show()

    def close(self, target=None):
        if target == "all":
            plt.close("all")
            self.current_figure = None
            self.current_axes_by_figure.clear()
            self.subplot_axes_by_figure.clear()
            return

        if target is None:
            figure_number = self.figure_number(self.current_figure)
            plt.close()
            self.current_figure = None
            if figure_number is not None:
                self.current_axes_by_figure.pop(figure_number, None)
                self.subplot_axes_by_figure.pop(figure_number, None)
            return

        plt.close(int(target))
        self.current_axes_by_figure.pop(int(target), None)
        self.subplot_axes_by_figure.pop(int(target), None)

        if (
            self.current_figure is not None
            and getattr(
                self.current_figure,
                "number",
                None,
            )
            == int(target)
        ):
            self.current_figure = None

    def plot(self, *arguments):
        series = parse_plot_arguments(arguments)

        self.ensure_current_figure()

        if not hasattr(self.current_figure, "gca"):
            lines = []

            for item in series:
                plotted = plt.plot(
                    item.x.tolist(),
                    item.y.tolist(),
                    **matplotlib_kwargs(item.properties),
                )

                if plotted is not None:
                    lines.extend(plotted)

            self.show()

            return lines

        axis = self.ensure_current_axes()

        if not self.hold_enabled:
            axis.cla()

        lines = []

        for item in series:
            plotted = axis.plot(
                item.x,
                item.y,
                **matplotlib_kwargs(item.properties),
            )
            lines.extend(plotted)

        self.show()

        return lines

    def histogram(self, *arguments):
        histogram_data = compute_histogram_from_arguments(arguments)
        return self.draw_histogram(histogram_data)

    def draw_histogram(self, histogram_data):
        self.ensure_current_figure()
        axis = self.ensure_current_axes()

        if not self.hold_enabled:
            axis.cla()

        artists = self.draw_histogram_artists(axis, histogram_data)
        histogram_data.Handle.matplotlib_artists = artists
        self.show()
        return histogram_data.Handle

    def draw_histogram_artists(self, axis, histogram_data):
        options = histogram_data.Options

        if options.DisplayStyle == "stairs":
            return self.draw_histogram_stairs(axis, histogram_data)

        return self.draw_histogram_bars(axis, histogram_data)

    def draw_histogram_bars(self, axis, histogram_data):
        options = histogram_data.Options
        edges = histogram_data.BinEdges
        values = histogram_data.Values
        widths = edges[1:] - edges[:-1]
        kwargs = {
            "align": "edge",
            "linewidth": options.LineWidth,
            "linestyle": options.LineStyle,
        }

        if options.DisplayName is not None:
            kwargs["label"] = options.DisplayName

        if options.LineStyle == "none":
            kwargs["linewidth"] = 0

        face_color = self.matplotlib_face_color(options)
        edge_color = self.matplotlib_edge_color(options)

        if face_color is not None:
            kwargs["color"] = face_color

        if edge_color is not None:
            kwargs["edgecolor"] = edge_color

        if options.Orientation == "horizontal":
            artists = axis.barh(
                edges[:-1],
                values,
                height=widths,
                **kwargs,
            )
        else:
            artists = axis.bar(
                edges[:-1],
                values,
                width=widths,
                **kwargs,
            )

        self.apply_histogram_patch_alpha(artists, options)
        return list(artists)

    def draw_histogram_stairs(self, axis, histogram_data):
        options = histogram_data.Options
        edges = histogram_data.BinEdges
        values = histogram_data.Values
        line_kwargs = {
            "linewidth": options.LineWidth,
            "linestyle": options.LineStyle,
        }

        if options.DisplayName is not None:
            line_kwargs["label"] = options.DisplayName

        edge_color = self.matplotlib_edge_color(options)

        if edge_color is not None:
            line_kwargs["color"] = edge_color

        if options.EdgeAlpha != 1.0:
            line_kwargs["alpha"] = options.EdgeAlpha

        if options.Orientation == "horizontal":
            x = np.repeat(values, 2)
            y = np.repeat(edges, 2)[1:-1]
        else:
            x = np.repeat(edges, 2)[1:-1]
            y = np.repeat(values, 2)

        (line,) = axis.plot(x, y, **line_kwargs)
        return [line]

    def matplotlib_face_color(self, options):
        if options.FaceColor == "auto":
            return None

        if options.FaceColor == "none":
            return "none"

        return options.FaceColor

    def matplotlib_edge_color(self, options):
        if options.EdgeColor == "auto":
            return None

        if options.EdgeColor == "none":
            return "none"

        return options.EdgeColor

    def apply_histogram_patch_alpha(self, artists, options):
        for artist in artists:
            if options.FaceColor != "none":
                artist.set_facecolor(
                    to_rgba(
                        artist.get_facecolor(),
                        options.FaceAlpha,
                    )
                )

            if options.EdgeColor != "none":
                artist.set_edgecolor(
                    to_rgba(
                        artist.get_edgecolor(),
                        options.EdgeAlpha,
                    )
                )

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
        self.current_figure, axes = plt.subplots(
            2,
            1,
            sharex=True,
        )

        axes[0].semilogx(frequency, magnitude_db)
        self.set_current_axes(axes[0])
        axes[0].set_title("Bode Diagram")
        axes[0].set_ylabel("Magnitude (dB)")
        axes[0].grid(True, which="both")

        axes[1].semilogx(frequency, phase_deg)
        axes[1].set_xlabel("Frequency (rad/s)")
        axes[1].set_ylabel("Phase (deg)")
        axes[1].grid(True, which="both")

        self.current_figure.tight_layout()

        self.show()

    def nyquist(self, real_values, imag_values):
        self.current_figure = plt.figure()
        axis = self.current_figure.add_subplot(111)
        self.set_current_axes(axis)

        axis.plot(real_values, imag_values)
        axis.axhline(0, color="0.6", linewidth=0.8)
        axis.axvline(0, color="0.6", linewidth=0.8)
        axis.plot([-1], [0], marker="x", color="red")
        axis.set_title("Nyquist Diagram")
        axis.set_xlabel("Real")
        axis.set_ylabel("Imaginary")
        axis.grid(True)
        axis.axis("equal")

        self.current_figure.tight_layout()

        self.show()

    def title(self, text):
        self.ensure_current_axes().set_title(str(text))
        self.refresh()

    def xlabel(self, text):
        self.ensure_current_axes().set_xlabel(str(text))
        self.refresh()

    def ylabel(self, text):
        self.ensure_current_axes().set_ylabel(str(text))
        self.refresh()

    def grid_on(self):
        self.ensure_current_axes().grid(True)
        self.refresh()

    def grid_off(self):
        self.ensure_current_axes().grid(False)
        self.refresh()

    def subplot(self, *arguments):
        figure = self.ensure_current_figure()
        spec = parse_subplot_arguments(arguments)
        axis = select_subplot_axis(self, figure, spec)
        self.refresh()
        return axis

    def xticks(self, *arguments):
        return self.ticks("x", *arguments)

    def yticks(self, *arguments):
        return self.ticks("y", *arguments)

    def ticks(self, dimension, *arguments):
        axis = self.ensure_current_axes()
        function_name = f"{dimension}ticks"

        if not arguments:
            return get_ticks(axis, dimension)

        if len(arguments) == 1 and isinstance(arguments[0], str):
            option = arguments[0].lower()

            if option == "mode":
                return get_tick_mode(axis, dimension)

            if option in {"auto", "manual"}:
                set_tick_mode(axis, dimension, option)
                self.refresh()
                return None

        if len(arguments) != 1:
            raise MathToolRuntimeError(
                f"{function_name}: expected zero or one argument"
            )

        set_ticks(
            axis,
            dimension,
            tick_values_from_argument(arguments[0], function_name),
        )
        self.refresh()
        return None

    def xticklabels(self, *arguments):
        return self.ticklabels("x", *arguments)

    def yticklabels(self, *arguments):
        return self.ticklabels("y", *arguments)

    def ticklabels(self, dimension, *arguments):
        axis = self.ensure_current_axes()
        function_name = f"{dimension}ticklabels"

        if not arguments:
            return get_ticklabels(axis, dimension)

        if len(arguments) == 1 and isinstance(arguments[0], str):
            option = arguments[0].lower()

            if option == "mode":
                return get_tick_label_mode(axis, dimension)

            if option in {"auto", "manual"}:
                set_tick_label_mode(axis, dimension, option)
                self.refresh()
                return None

        labels = tick_labels_from_arguments(
            arguments,
            function_name,
            len(get_ticks(axis, dimension)),
        )
        set_ticklabels(axis, dimension, labels)
        self.refresh()
        return None

    def xline(self, *arguments):
        return self.reference_line("x", *arguments)

    def yline(self, *arguments):
        return self.reference_line("y", *arguments)

    def reference_line(self, dimension, *arguments):
        function_name = f"{dimension}line"
        axis = self.ensure_current_axes()
        coordinates, properties, labels = parse_reference_line_arguments(
            arguments,
            function_name,
        )
        kwargs = reference_line_kwargs(properties)
        lines = []

        for index, coordinate in enumerate(coordinates):
            if dimension == "x":
                line = axis.axvline(coordinate, **kwargs)
                self.add_reference_label(
                    axis,
                    dimension,
                    coordinate,
                    label_for_index(labels, index),
                    properties,
                )
            else:
                line = axis.axhline(coordinate, **kwargs)
                self.add_reference_label(
                    axis,
                    dimension,
                    coordinate,
                    label_for_index(labels, index),
                    properties,
                )

            lines.append(line)

        self.refresh()
        return lines[0] if len(lines) == 1 else lines

    def add_reference_label(
        self,
        axis,
        dimension,
        coordinate,
        label,
        properties,
    ):
        if label is None:
            return

        horizontal, vertical = text_alignment(properties, dimension)
        rotation = text_rotation(properties, dimension)

        if dimension == "x":
            axis.text(
                coordinate,
                1.0,
                label,
                transform=axis.get_xaxis_transform(),
                ha=horizontal,
                va=vertical,
                rotation=rotation,
            )
        else:
            axis.text(
                1.0,
                coordinate,
                label,
                transform=axis.get_yaxis_transform(),
                ha=horizontal,
                va=vertical,
                rotation=rotation,
            )

    def legend(self, *arguments):
        axis = self.ensure_current_axes()
        command, labels, properties = parse_legend_arguments(arguments)

        existing = axis.get_legend()

        if command == "off":
            if existing is not None:
                existing.remove()
            self.refresh()
            return None

        if command == "hide":
            if existing is not None:
                existing.set_visible(False)
            self.refresh()
            return existing

        if command == "show" and existing is not None:
            existing.set_visible(True)
            self.refresh()
            return existing

        kwargs = legend_kwargs(properties, len(labels))

        if labels:
            legend = axis.legend(labels, **kwargs)
        else:
            legend = axis.legend(**kwargs)

        apply_legend_text_options(legend, properties)
        self.refresh()
        return legend

    def axis(self, *arguments):
        axis = self.ensure_current_axes()
        result, changed = apply_matplotlib_axis(axis, *arguments)

        if changed:
            self.refresh()

        return result

    def ensure_current_figure(self):
        if self.current_figure is None:
            self.current_figure = plt.figure()
        else:
            plt.figure(self.current_figure.number)

        return self.current_figure

    def ensure_current_axes(self):
        figure = self.ensure_current_figure()
        figure_number = self.figure_number(figure)
        axis = self.current_axes_by_figure.get(figure_number)

        if axis is not None and axis in getattr(figure, "axes", []):
            plt.sca(axis)
            return axis

        if getattr(figure, "axes", None):
            axis = figure.axes[-1]
        else:
            axis = figure.add_subplot(111)

        self.set_current_axes(axis)
        return axis

    def restore_current_axes(self):
        if self.current_figure is None:
            return

        figure_number = self.figure_number(self.current_figure)
        axis = self.current_axes_by_figure.get(figure_number)

        if axis is not None and axis in getattr(
            self.current_figure,
            "axes",
            [],
        ):
            plt.sca(axis)

    def set_current_axes(self, axis):
        if self.current_figure is None:
            self.current_figure = axis.figure

        figure_number = self.figure_number(axis.figure)
        self.current_axes_by_figure[figure_number] = axis
        plt.sca(axis)

    def subplot_axes_for_current_figure(self):
        figure_number = self.figure_number(self.current_figure)

        return self.subplot_axes_by_figure.setdefault(
            figure_number,
            {},
        )

    def figure_number(self, figure):
        return getattr(figure, "number", None)

    def show(self):
        plt.show(block=False)
        self.refresh()

    def refresh(self):
        figure = plt.gcf()

        if figure is None:
            return

        canvas = getattr(figure, "canvas", None)

        if canvas is None:
            return

        canvas.draw_idle()
        canvas.flush_events()
