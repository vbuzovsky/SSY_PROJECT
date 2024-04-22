from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QMainWindow, QApplication, QTextEdit, QSplitter
from PySide6.QtCore import QRunnable, Slot, Signal, QObject, QThreadPool
from PySide6.QtCore import Qt
from components.canvas import MplCanvas
from components.detail_info import DetailInfo
from components.network_node import NetworkNode

from UART_parser import parse
from helpers.config_helper import get_config_dict
from helpers.parse_output_into_nodeinfo import build_node_information

import sys
import time
import serial
from graph import NetworkGraph

PORT = "COM3"
BAUDRATE = 38400
RES_WIDTH = 1280
RES_HEIGHT = 720

mock_message = [
    [
        [('Command_ID', 'uint8'), ['0x01']],
        [('NodeType', 'uint8'), ['0x00']], 
        [('FullAddress', 'uint64'), ['0x00', '0x00', '0x00', '0x00', '0x00', '0x00', '0x00', '0x00']],
        [('ShortAddress', 'uint16'), ['0x00', '0x00']],
        [('SoftwareVersion', 'uint32'), ['0x00', '0x01', '0x01', '0x01']],
        [('ChannelMask', 'uint32'), ['0x00', '0x80', '0x00', '0x00']],
        [('PanID', 'uint16'), ['0x34', '0x12']], 
        [('WorkingChannel', 'uint8'), ['0x0f']],
        [('ParentAddress', 'uint16'), ['0xff', '0xff']],
        [('LQI', 'uint8'), ['0x00']],
        [('RSSI', 'int8'), ['0x00']]
    ],
    [
        ['0x01', 
            ['0x31', '0x31', '0x00', '0x00', '0xc', '0x00', '0x00', '0x00', '0xee', '0x00', '0x00', '0x00']], 
        ['0x20', 
            ['0x43', '0x6f', '0x6f', '0x72', '0x64', '0x69', '0x6e', '0x61', '0x74', '0x6f', '0x72']]
    ]
]

class PrintWorkerSignals(QObject):
    '''
    Defines the signal for printing the current state of network nodes
    '''
    finished = Signal()
    print_nodes = Signal(set)

class PrintWorker(QRunnable):
    '''
    Worker thread for periodically printing the current state of network nodes

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
    '''
    
    def __init__(self, nodes, *args, **kwargs):
        super(PrintWorker, self).__init__()
        self._is_running = True
        self.nodes = nodes
        self.signals = PrintWorkerSignals()

    @Slot()
    def run(self):
        '''
        Infinite loop to keep the thread running, printing current state of network nodes
        '''
        while self._is_running:
            self.signals.print_nodes.emit(self.nodes)
            time.sleep(10)
            # TODO: THIS IS WHERE THE GRAPH SHOULD BE "REBUIL"

        self.signals.finished.emit()  # Done
    
    @Slot()
    def stop(self):
        self._is_running = False


class ParseWorkerSignals(QObject):
    '''
    Defines the progress signal (from parser) used for passing around data
    
    '''
    finished = Signal()
    progress = Signal(list)



class ParseWorker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
    '''
    
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
        '''
        Infinite loop to keep the thread running, parsing data from serial port
        '''

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

        self.network_graph = NetworkGraph()
        self.network_graph.G.add_node(1)
        self.network_graph.G.add_node(2)
        self.network_graph.G.add_edge(1, 2)
        self.canvas = MplCanvas(self.canvas_panel, width=180, height=190, dpi=100, graph=self.network_graph.G)
        self.canvas_layout.addWidget(self.canvas)
        self.canvas_panel.setLayout(self.canvas_layout)

        mock_node = NetworkNode(header=mock_message[0], data=mock_message[1])
        detail_info = DetailInfo(mock_node)
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
        full_address = node_info["FullAddress"]
        if full_address not in self.network_graph.get_nodes():
            self.network_graph.add_node(full_address, node_info)

        # TODO: THIS NEED FIXING
        # PARENT ADDR IS 2B FULL IS 8B THIS WONT WORK
        if node_info["ParentAddress"] in self.network_graph.get_nodes():
            self.network_graph.add_edge(full_address, node_info["ParentAddress"])
    
        
    def work(self):
        # Disable start button and enable stop button
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        # Pass the function to execute
        self.parse_worker = ParseWorker(parse) 
        self.parse_worker.signals.progress.connect(self.new_data_incoming)

        self.print_worker = PrintWorker(self.network_graph.get_nodes())
        self.print_worker.signals.print_nodes.connect(self.print_nodes_state)


        # Execute
        self.threadpool.start(self.parse_worker)
        self.threadpool.start(self.print_worker)

    def print_nodes_state(self, nodes):
        new_graph = NetworkGraph()
        for node in nodes:
            new_graph.add_node(node, {"someinfo": "idk"})
        print("Current state of network nodes:")
        for node in nodes:
            print(node)
        print("\nRebuiling graph...")
        self.canvas.update_graph(new_graph.G)

    # TODO: THIS DOESNT WORK AT ALL, STILL RUNNING AFTER STOP CLICKED
    def stop_work(self):
        self.parse_worker.stop()
        self.print_worker.stop()

        # Enable start button and disable stop button
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)


app = QApplication(sys.argv)
window = MainWindow()
app.exec()