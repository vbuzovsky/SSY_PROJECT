from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from netgraph import InteractiveGraph
from matplotlib.figure import Figure

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=3, height=1, dpi=100, graph=None):
        super(MplCanvas, self).__init__(Figure(figsize=(width, height), dpi=dpi, constrained_layout=True))
        self.setParent(parent)
        self.ax = self.figure.add_subplot(111)
        self.graph = graph
        self.plot_instance = None
        self.update_graph(graph)

    def update_graph(self, graph):
        if self.plot_instance is not None:
            self.ax.clear() 
        self.plot_instance = InteractiveGraph(graph, ax=self.ax)
        self.figure.canvas.draw_idle()  # Redraw the canvas