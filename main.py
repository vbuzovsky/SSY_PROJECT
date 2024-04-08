from PySide6.QtWidgets import QVBoxLayout, QPushButton, QWidget, QMainWindow, QApplication, QTextEdit, QSplitter
from PySide6.QtCore import QRunnable, Slot, Signal, QObject, QThreadPool
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from netgraph import InteractiveGraph
import networkx as nx
from matplotlib.figure import Figure

from UART_parser import parse

import sys
import serial

PORT = "COM3"
BAUDRATE = 38400

class WorkerSignals(QObject):
    '''
    Defines the progress signal (from parser) used for passing around data
    
    '''
    progress = Signal(list)



class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
    '''
    
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        self.fn = fn # EXEC THIS IN NEW THREAD
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['callback'] = self.signals.progress

    @Slot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        ser_settings = {
            "port": PORT,
            "baudrate": BAUDRATE,
            "parity": serial.PARITY_NONE,
            "stopbits": serial.STOPBITS_ONE,
            "bytesize": serial.EIGHTBITS,
            "timeout": 0
        }

        while True:
            data = self.fn(ser_settings, self.signals.progress)
            self.signals.result.emit(data)

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=100, height=100, dpi=100):
        super(MplCanvas, self).__init__(Figure(figsize=(width, height), dpi=dpi))
        self.setParent(parent)
        self.ax = self.figure.add_subplot(111)
        graph = nx.house_x_graph()
        self.plot_instance = InteractiveGraph(graph, ax=self.ax)

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setFixedHeight(720)
        self.setFixedWidth(1280)

        main_layout = QVBoxLayout()

        splitter = QSplitter()  
        splitter.setOrientation(Qt.Vertical) 

        text_panel = QWidget()
        text_layout = QVBoxLayout()
        self.text_area = QTextEdit()
        text_layout.addWidget(self.text_area)
        text_panel.setLayout(text_layout)

        canvas_panel = QWidget()
        canvas_layout = QVBoxLayout()
        self.canvas = MplCanvas(canvas_panel, width=5, height=4, dpi=100)
        canvas_layout.addWidget(self.canvas)
        canvas_panel.setLayout(canvas_layout)


        splitter.addWidget(text_panel)
        splitter.addWidget(canvas_panel)

        main_layout.addWidget(splitter)

        self.button = QPushButton("Start Work")
        self.button.clicked.connect(self.work)
        main_layout.addWidget(self.button)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.show()

        self.threadpool = QThreadPool()

    def new_data_incoming(self, data):
        # Update QTextEdit with the received data
        self.text_area.append(str(data))  

    def work(self):
        # Pass the function to execute
        worker = Worker(parse) 
        worker.signals.progress.connect(self.new_data_incoming)

        # Execute
        self.threadpool.start(worker)


app = QApplication(sys.argv)
window = MainWindow()
app.exec()