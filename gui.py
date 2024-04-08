from PySide6.QtWidgets import QVBoxLayout, QPushButton, QWidget, QMainWindow, QApplication, QTextEdit
from PySide6.QtCore import QRunnable, Slot, Signal, QObject, QThreadPool
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


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.layout = QVBoxLayout()

        self.text_area = QTextEdit()
        self.layout.addWidget(self.text_area)

        self.button = QPushButton("Start Work")
        self.button.clicked.connect(self.work)
        self.layout.addWidget(self.button)

        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)
        self.show()

        self.threadpool = QThreadPool()

    def progress_fn(self, data):
        # Update QTextEdit with the received data
        self.text_area.append(str(data))  

    def work(self):
        # Pass the function to execute
        worker = Worker(parse) 
        worker.signals.progress.connect(self.progress_fn)

        # Execute
        self.threadpool.start(worker)


app = QApplication(sys.argv)
window = MainWindow()
app.exec()