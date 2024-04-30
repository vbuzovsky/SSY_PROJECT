import sys
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout


class DetailInfo(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.labels = {}

    def add_label(self, label_text, data):
        if label_text in self.labels:
            line_edit = self.labels[label_text]
            line_edit.setText(data)
        else:
            label = QLabel(label_text)
            line_edit = QLineEdit(data)
            line_edit.setReadOnly(True)
            hbox = QHBoxLayout()
            hbox.addWidget(label)
            hbox.addWidget(line_edit)
            self.layout().addLayout(hbox)
            self.labels[label_text] = line_edit

    def name_to_ascii(self, hex_string):
        ascii_string = ""
        for i in range(0, len(hex_string), 2):
            hex_char = hex_string[i:i+2]
            ascii_char = chr(int(hex_char, 16))
            ascii_string += ascii_char
        return ascii_string[::-1]  

    def update_detail_info(self, event, plot_instance, graph):
        print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
                ('double' if event.dblclick else 'single', event.button,
                event.x, event.y, event.xdata, event.ydata))
        x = event.xdata
        y = event.ydata
        clicked_node = None
        for node_id, node_artist in plot_instance.node_artists.items():
            dist = ((x - node_artist.xy[0])**2 + (y - node_artist.xy[1])**2)**0.5
            if dist < node_artist.radius:
                clicked_node = node_id
                break

        if clicked_node is not None:
            #print("Clicked node:", clicked_node)
            node_info = graph.nodes[clicked_node]
            #print("Additional info:", node_info)  
            for key, value in node_info.items():
                if(key == "Node name"):
                    value = self.name_to_ascii(value)
                self.add_label(key, value)
