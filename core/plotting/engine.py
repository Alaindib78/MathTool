import matplotlib.pyplot as plt


class PlotEngine:
    def __init__(self):
        self.current_figure = None

    def plot(self, x, y):
        self.current_figure = plt.figure()

        plt.plot(x, y)

        plt.show()

    def title(self, text):
        plt.title(text)

    def xlabel(self, text):
        plt.xlabel(text)

    def ylabel(self, text):
        plt.ylabel(text)

    def grid_on(self):
        plt.grid(True)

    def grid_off(self):
        plt.grid(False)