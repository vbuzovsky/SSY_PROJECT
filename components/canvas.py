from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from netgraph import InteractiveGraph
from matplotlib.figure import Figure

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=3, height=1, dpi=100, graph=None):
        super(MplCanvas, self).__init__(Figure(figsize=(width, height), dpi=dpi, constrained_layout=True))
        self.setParent(parent)
        self.ax = self.figure.add_subplot(111)
        self.plot_instance = InteractiveGraph(graph, ax=self.ax)

        