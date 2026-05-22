from PySide6.QtCore import QObject, Qt, Signal, Slot

from core.plotting.engine import PlotEngine


class GuiPlotEngine(QObject):
    request = Signal(str, object)

    def __init__(self):
        super().__init__()

        self.engine = PlotEngine()

        self.request.connect(
            self.handle_request,
            Qt.QueuedConnection
        )

    def plot(self, x, y):
        self.request.emit("plot", (x, y))

    def bode(self, frequency, magnitude_db, phase_deg):
        self.request.emit(
            "bode",
            (frequency, magnitude_db, phase_deg),
        )

    def nyquist(self, real_values, imag_values):
        self.request.emit(
            "nyquist",
            (real_values, imag_values),
        )

    def figure(self, number=None):
        self.request.emit("figure", (number,))

    def close(self, target=None):
        self.request.emit("close", (target,))

    def title(self, text):
        self.request.emit("title", (text,))

    def xlabel(self, text):
        self.request.emit("xlabel", (text,))

    def ylabel(self, text):
        self.request.emit("ylabel", (text,))

    def grid_on(self):
        self.request.emit("grid_on", ())

    def grid_off(self):
        self.request.emit("grid_off", ())

    @Slot(str, object)
    def handle_request(self, method_name, arguments):
        method = getattr(self.engine, method_name)

        method(*arguments)
