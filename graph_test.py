import sys

from PyQt5 import QtWidgets

import matplotlib

matplotlib.use("Qt5Agg")


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

from netgraph import InteractiveGraph

import networkx as nx


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        super(MplCanvas, self).__init__(Figure(figsize=(width, height), dpi=dpi))
        self.setParent(parent)
        self.ax = self.figure.add_subplot(111)
        graph = nx.house_x_graph()
        self.plot_instance = InteractiveGraph(graph, ax=self.ax)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        widget = QtWidgets.QWidget()
        self.setCentralWidget(widget)

        layout = QtWidgets.QVBoxLayout(widget)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec_()


if __name__ == "__main__":
    main()