# gui.py

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit
from multiprocessing import Pipe

def run_gui(gui_pipe):
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Serial Data Viewer")
    window.setGeometry(100, 100, 600, 400)

    text_edit = QTextEdit()
    window.setCentralWidget(text_edit)
    window.show()

    def update_text(data):
        text_edit.append(str(data))

    while True:
        app.processEvents()  # Process GUI events to keep the GUI responsive
        if gui_pipe.poll():  # Check if there is data in the pipe
            data = gui_pipe.recv()  # Receive data from the pipe
            update_text(data)

    sys.exit(app.exec_())
