import matplotlib.pyplot as plt

from core.plotting.line_spec import matplotlib_kwargs
from core.plotting.plot_parser import parse_plot_arguments


class PlotEngine:
    def __init__(self):
        self.current_figure = None
        self.hold_enabled = False

    def figure(self, number=None):
        self.current_figure = plt.figure(
            None if number is None else int(number)
        )

        self.show()

    def close(self, target=None):
        if target == "all":
            plt.close("all")
            self.current_figure = None
            return

        if target is None:
            plt.close()
            self.current_figure = None
            return

        plt.close(int(target))

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

        if self.current_figure is None:
            self.current_figure = plt.figure()
        else:
            plt.figure(self.current_figure.number)

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

        axis = plt.gca()

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
        plt.title(text)
        self.refresh()

    def xlabel(self, text):
        plt.xlabel(text)
        self.refresh()

    def ylabel(self, text):
        plt.ylabel(text)
        self.refresh()

    def grid_on(self):
        plt.grid(True)
        self.refresh()

    def grid_off(self):
        plt.grid(False)
        self.refresh()

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
