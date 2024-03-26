import sys
import random
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget
from PySide6.QtGui import QImage, QPainter, QPixmap
from PySide6.QtCore import Qt, QPoint


class Canvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = QImage(800, 800, QImage.Format_RGB32)
        self.image.fill(Qt.white)
        self.cat_image = QPixmap("misc/node.png") 

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image)

    def paint_cats(self, positions):
        painter = QPainter(self.image)
        for position in positions:
            painter.drawPixmap(position, self.cat_image)


class TabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas = Canvas(self)
        self.addTab(self.canvas, "Canvas")

        self.tab1 = QWidget()
        self.addTab(self.tab1, "log")

        self.tab2 = QWidget()
        self.addTab(self.tab2, "other")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WSN Visualizer")
        self.setGeometry(100, 100, 600, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)
        self.tab_widget = TabWidget(self.central_widget)
        self.layout.addWidget(self.tab_widget)

        self.add_cats_to_canvas()

    def add_cats_to_canvas(self):
        positions = [QPoint(random.randint(50, 350), random.randint(50, 350)) for _ in range(5)]
        self.tab_widget.canvas.paint_cats(positions)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
