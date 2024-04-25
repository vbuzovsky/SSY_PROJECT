from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from netgraph import InteractiveGraph
from matplotlib.figure import Figure
from .detail_info import DetailInfo
import threading

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=3, height=1, dpi=100, graph=None, update_info=None):
        super(MplCanvas, self).__init__(Figure(figsize=(width, height), dpi=dpi, constrained_layout=True))
        self.setParent(parent)
        self.ax = self.figure.add_subplot(111)
        self.graph = graph
        self.update_info = update_info
        self.plot_instance = None
        self.update_graph(graph)
        self.click_thread = None

    def update_graph(self, graph):
        if self.plot_instance is not None:
            self.ax.clear() 
        self.plot_instance = InteractiveGraph(graph, ax=self.ax)

        self.figure.canvas.mpl_connect("button_press_event", self.on_click_event)
        self.figure.canvas.draw_idle()  # Redraw the canvas

    def on_click_event(self, event):
        self.update_info.update_detail_info(event, self.plot_instance, self.graph)


