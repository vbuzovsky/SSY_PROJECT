import threading
import UART_parser
import ui

if __name__ == "__main__":
    thread1 = threading.Thread(target=UART_parser.parse)
    thread2 = threading.Thread(target=ui.print_data)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()