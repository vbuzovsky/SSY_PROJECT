import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout

class DetailInfo(QWidget):
    def __init__(self, node):
        super().__init__()
        self.node = node
        layout = QVBoxLayout()
        self.setLayout(layout)

        for node_info in node.header:
            if not node_info[0][0] == 'Command_ID':
                self.add_label(str(node_info[0][0]), str(self.hex_to_dec(node_info[1])))

    # TODO: this and few other methods maybe belond to the NetworkNode class
    def hex_to_dec(self, hex_list):
        return [int(x, 16) for x in hex_list]

    def add_label(self, label_text, data):
        label = QLabel(label_text)
        line_edit = QLineEdit(data)
        line_edit.setReadOnly(True)

        hbox = QHBoxLayout()
        hbox.addWidget(label)
        hbox.addWidget(line_edit)

        self.layout().addLayout(hbox)