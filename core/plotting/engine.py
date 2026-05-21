import matplotlib.pyplot as plt


class PlotEngine:
    def __init__(self):
        self.current_figure = None

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

    def plot(self, x, y):
        if self.current_figure is None:
            self.current_figure = plt.figure()
        else:
            plt.figure(self.current_figure.number)

        plt.plot(x, y)

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
