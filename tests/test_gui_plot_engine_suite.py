from gui.plot_engine import GuiPlotEngine


class FakeEngine:
    def __init__(self):
        self.calls = []

    def plot(self, x, y):
        self.calls.append(("plot", x, y))

    def bode(self, frequency, magnitude_db, phase_deg):
        self.calls.append(("bode", frequency, magnitude_db, phase_deg))

    def nyquist(self, real_values, imag_values):
        self.calls.append(("nyquist", real_values, imag_values))

    def figure(self, number=None):
        self.calls.append(("figure", number))

    def close(self, target=None):
        self.calls.append(("close", target))

    def title(self, text):
        self.calls.append(("title", text))

    def xlabel(self, text):
        self.calls.append(("xlabel", text))

    def ylabel(self, text):
        self.calls.append(("ylabel", text))

    def grid_on(self):
        self.calls.append(("grid_on",))

    def grid_off(self):
        self.calls.append(("grid_off",))


def test_gui_plot_engine_forwards_plot_requests_to_core_engine():
    gui_engine = GuiPlotEngine()
    fake_engine = FakeEngine()
    gui_engine.engine = fake_engine

    gui_engine.handle_request("figure", (2,))
    gui_engine.handle_request("plot", ([1], [2]))
    gui_engine.handle_request("bode", ([1], [2], [3]))
    gui_engine.handle_request("nyquist", ([1], [2]))
    gui_engine.handle_request("title", ("Title",))
    gui_engine.handle_request("xlabel", ("x",))
    gui_engine.handle_request("ylabel", ("y",))
    gui_engine.handle_request("grid_on", ())
    gui_engine.handle_request("grid_off", ())
    gui_engine.handle_request("close", ("all",))

    assert fake_engine.calls == [
        ("figure", 2),
        ("plot", [1], [2]),
        ("bode", [1], [2], [3]),
        ("nyquist", [1], [2]),
        ("title", "Title"),
        ("xlabel", "x"),
        ("ylabel", "y"),
        ("grid_on",),
        ("grid_off",),
        ("close", "all"),
    ]
