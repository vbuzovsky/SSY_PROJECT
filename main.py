from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QMainWindow, QApplication, QTextEdit, QSplitter
from PySide6.QtCore import QRunnable, Slot, Signal, QObject, QThreadPool
from PySide6.QtCore import Qt
from components.canvas import MplCanvas
from components.detail_info import DetailInfo
from components.network_node import NetworkNode

from UART_parser import parse

import sys
import serial

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

class ParseWorkerSignals(QObject):
    '''
    Defines the progress signal (from parser) used for passing around data
    
    '''
    progress = Signal(list)



class ParseWorker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
    '''
    
    def __init__(self, fn, *args, **kwargs):
        super(ParseWorker, self).__init__()

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

        while True:
            data = self.fn(ser_settings, self.signals.progress)
            self.signals.result.emit(data)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setFixedHeight(RES_HEIGHT)
        self.setFixedWidth(RES_WIDTH)

        self.network_nodes = set()
        main_layout = QVBoxLayout()

        splitter = QSplitter()  
        splitter.setOrientation(Qt.Horizontal) 

        text_panel = QWidget()
        text_panel.setFixedWidth(RES_WIDTH/3) 
        text_layout = QVBoxLayout()
        self.text_area = QTextEdit()
        text_layout.addWidget(self.text_area)
        text_panel.setLayout(text_layout)

        canvas_panel = QWidget()
        canvas_panel.setFixedWidth(RES_WIDTH/3*2) 
        canvas_layout = QVBoxLayout()
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        self.canvas = MplCanvas(canvas_panel, width=180, height=190, dpi=100)
        canvas_layout.addWidget(self.canvas)
        canvas_panel.setLayout(canvas_layout)

        mock_node = NetworkNode(header=mock_message[0], data=mock_message[1])
        detail_info = DetailInfo(mock_node)
        splitter.addWidget(detail_info)
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
        potential_node = NetworkNode(header=data[0], data=data[1])
        self.network_nodes.add(potential_node) # should not be added, if exists

    def work(self):
        # Pass the function to execute
        worker = ParseWorker(parse) 
        worker.signals.progress.connect(self.new_data_incoming)

        # Execute
        self.threadpool.start(worker)


app = QApplication(sys.argv)
window = MainWindow()
app.exec()