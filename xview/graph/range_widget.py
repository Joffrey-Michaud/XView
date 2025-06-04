from PyQt5.QtWidgets import QCheckBox, QWidget, QHBoxLayout, QLabel, QVBoxLayout, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QIcon
from xview import get_config_file, set_config_file, set_config_data


class RangeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # region - x-axis range
        self.x_widget = QWidget()
        self.x_layout = QHBoxLayout()
        self.x_widget.setLayout(self.x_layout)

        self.x_label = QLabel("X-Axis range:")
        self.x_layout.addWidget(self.x_label)
        self.x_min = QLineEdit()
        self.x_min.setPlaceholderText("Min")
        self.x_layout.addWidget(self.x_min)
        self.x_layout.addWidget(QLabel("-"))
        self.x_max = QLineEdit()
        self.x_max.setPlaceholderText("Max")
        self.x_layout.addWidget(self.x_max)
        self.layout.addWidget(self.x_widget)

        # region - y-axis range
        self.y_widget = QWidget()
        self.y_layout = QHBoxLayout()
        self.y_widget.setLayout(self.y_layout)

        self.y_label = QLabel("Y-Axis range:")
        self.y_layout.addWidget(self.y_label)
        self.y_min = QLineEdit()
        self.y_min.setPlaceholderText("Min")
        self.y_layout.addWidget(self.y_min)
        self.y_layout.addWidget(QLabel("-"))
        self.y_max = QLineEdit()
        self.y_max.setPlaceholderText("Max")
        self.y_layout.addWidget(self.y_max)
        self.layout.addWidget(self.y_widget)

        # region - normalize
        self.normalize_widget = QWidget()
        self.normalize_layout = QHBoxLayout()
        self.normalize_widget.setLayout(self.normalize_layout)
        self.normalize_label = QLabel("Normalize:")
        self.normalize_layout.addWidget(self.normalize_label)
        self.normalize_checkbox = QCheckBox()
        self.normalize_layout.addWidget(self.normalize_checkbox)
        self.layout.addWidget(self.normalize_widget)

    # def set_
