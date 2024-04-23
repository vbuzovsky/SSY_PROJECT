from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from netgraph import InteractiveGraph
from matplotlib.figure import Figure

import threading

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=3, height=1, dpi=100, graph=None):
        super(MplCanvas, self).__init__(Figure(figsize=(width, height), dpi=dpi, constrained_layout=True))
        self.setParent(parent)
        self.ax = self.figure.add_subplot(111)
        self.graph = graph
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
        if self.click_thread is None or not self.click_thread.is_alive():
            self.click_thread = threading.Thread(target=self.handle_click, args=(event,))
            self.click_thread.start()

    def handle_click(self, event):
        print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
                ('double' if event.dblclick else 'single', event.button,
                event.x, event.y, event.xdata, event.ydata))
        x = event.xdata
        y = event.ydata
        clicked_node = None
        for node_id, node_artist in self.plot_instance.node_artists.items():
            dist = ((x - node_artist.xy[0])**2 + (y - node_artist.xy[1])**2)**0.5
            if dist < node_artist.radius:
                clicked_node = node_id
                break

        if clicked_node is not None:
            print("Clicked node:", clicked_node)


