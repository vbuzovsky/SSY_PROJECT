# main.py

import serial
import sys
from multiprocessing import Process, Pipe
from UART_parser import parse
from gui import run_gui

PORT = "COM3"
BAUDRATE = 38400

def main():
    ser_settings = {
        "port": PORT,
        "baudrate": BAUDRATE,
        "parity": serial.PARITY_NONE,
        "stopbits": serial.STOPBITS_ONE,
        "bytesize": serial.EIGHTBITS,
        "timeout": 0
    }

    # Create a Pipe for communication between parser and GUI
    parser_pipe, gui_pipe = Pipe()

    # Start GUI process
    gui_process = Process(target=run_gui, args=(gui_pipe,))
    gui_process.start()

    # Start parser process
    parser_process = Process(target=parse, args=(ser_settings, parser_pipe))
    parser_process.start()

    try:
        parser_process.join()  # Wait for the parser process to finish
        gui_process.terminate()  # Terminate the GUI process after parser finishes
    except KeyboardInterrupt:
        print("Closing application...")
        parser_process.terminate()
        gui_process.terminate()
        sys.exit(0)

if __name__ == "__main__":
    main()
