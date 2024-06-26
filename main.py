from PySide6.QtWidgets import QVBoxLayout, QPushButton, QWidget, QMainWindow, QApplication, QTextEdit, QSplitter
from PySide6.QtCore import QRunnable, Slot, Signal, QObject, QThreadPool
from PySide6.QtCore import Qt
from components.canvas import MplCanvas
from components.detail_info import DetailInfo

from UART_parser import parse
from helpers.parse_output_into_nodeinfo import build_node_information
import sys
import time
import serial
from graph import NetworkGraph

PORT = "COM3"
BAUDRATE = 38400
RES_WIDTH = 1280
RES_HEIGHT = 720


class GraphRebuilderSignals(QObject):
    finished = Signal()
    force_rebuild = Signal(set)

class GraphRebuildWorker(QRunnable):
    def __init__(self, nodes, *args, **kwargs):
        super(GraphRebuildWorker, self).__init__()
        self._is_running = True
        self.nodes = nodes
        self.signals = GraphRebuilderSignals()

    @Slot()
    def run(self):
        while self._is_running:
            self.signals.force_rebuild.emit(self.nodes)
            time.sleep(10)

        self.signals.finished.emit()  # Done
    
    @Slot()
    def stop(self):
        self._is_running = False


class ParseWorkerSignals(QObject):
    finished = Signal()
    progress = Signal(list)


class ParseWorker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(ParseWorker, self).__init__()
        self._is_running = True
        self.fn = fn # EXEC THIS IN NEW THREAD
        self.args = args
        self.kwargs = kwargs
        self.signals = ParseWorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['callback'] = self.signals.progress

    @Slot()
    def run(self):
        ser_settings = {
            "port": PORT,
            "baudrate": BAUDRATE,
            "parity": serial.PARITY_NONE,
            "stopbits": serial.STOPBITS_ONE,
            "bytesize": serial.EIGHTBITS,
            "timeout": 0
        }

        while self._is_running:
            data = self.fn(ser_settings, self.signals.progress)
            self.signals.result.emit(data)

        self.signals.finished.emit()

    @Slot()
    def stop(self):
        self._is_running = False


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setFixedHeight(RES_HEIGHT)
        self.setFixedWidth(RES_WIDTH)
        self.setWindowTitle("WSN Demo 2.0")
        main_layout = QVBoxLayout()
        splitter = QSplitter()  
        splitter.setOrientation(Qt.Horizontal) 

        text_panel = QWidget()
        text_panel.setFixedWidth(RES_WIDTH/3) 
        text_layout = QVBoxLayout()
        self.text_area = QTextEdit()
        text_layout.addWidget(self.text_area)
        text_panel.setLayout(text_layout)

        self.canvas_panel = QWidget()
        self.canvas_panel.setFixedWidth(RES_WIDTH/3*2) 
        self.canvas_layout = QVBoxLayout()
        self.canvas_layout.setContentsMargins(0, 0, 0, 0)

        detail_info = DetailInfo()

        self.network_graph = NetworkGraph()
        self.network_graph.G.add_node("1")
        self.previous_graph_nodes = self.network_graph.get_nodes()

        self.canvas = MplCanvas(self.canvas_panel, width=180, height=190, dpi=100, graph=self.network_graph.G, update_info=detail_info)
        self.canvas_layout.addWidget(self.canvas)
        self.canvas_panel.setLayout(self.canvas_layout)

        splitter.addWidget(detail_info)
        splitter.addWidget(self.canvas_panel)

        main_layout.addWidget(splitter)

        self.start_button = QPushButton("Start Work")
        self.start_button.clicked.connect(self.work)
        main_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Work")
        self.stop_button.clicked.connect(self.stop_work)
        main_layout.addWidget(self.stop_button)
        self.stop_button.setEnabled(False)  # Initially disable stop button

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.show()

        self.threadpool = QThreadPool()

    def new_data_incoming(self, data):
        node_info = build_node_information(data)
        short_address = node_info["ShortAddress"]
        if short_address not in self.network_graph.get_nodes():
            if("1" in self.network_graph.get_nodes()): #TODO: awful hack to remove inital node, graph cannot be printed with no nodes. needs fix
                self.network_graph.G.remove_node("1")
            self.network_graph.add_node(short_address, node_info)
            if(node_info['ParentAddress'] == "ffff" and node_info['ShortAddress'] != "0000"):
                self.network_graph.G.add_edge(short_address, "0000") # autoconnect to coordinator

        if node_info["ParentAddress"] in self.network_graph.get_nodes():
            self.network_graph.G.add_edge(short_address, node_info["ParentAddress"])
    
        
    def work(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        # Pass the function to execute
        self.parse_worker = ParseWorker(parse) 
        self.parse_worker.signals.progress.connect(self.new_data_incoming)

        self.print_worker = GraphRebuildWorker(self.network_graph)
        self.print_worker.signals.force_rebuild.connect(self.rebuild_graph)

        self.threadpool.start(self.parse_worker)
        self.threadpool.start(self.print_worker)

    def rebuild_graph(self, graph):
        self.canvas.update_graph(graph.G)
               

    # TODO: THIS DOESNT WORK AT ALL, STILL RUNNING AFTER STOP CLICKED
    def stop_work(self):
        self.parse_worker.stop()
        self.print_worker.stop()

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)


app = QApplication(sys.argv)
window = MainWindow()
app.exec()