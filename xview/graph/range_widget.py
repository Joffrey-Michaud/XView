from PyQt5.QtWidgets import QCheckBox, QWidget, QHBoxLayout, QLabel, QVBoxLayout, QLineEdit


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

        self.boxes_widget = QWidget()
        self.boxes_layout = QHBoxLayout()
        self.boxes_widget.setLayout(self.boxes_layout)
        

        # region - normalize
        self.normalize_widget = QWidget()
        self.normalize_layout = QHBoxLayout()
        self.normalize_widget.setLayout(self.normalize_layout)
        self.normalize_label = QLabel("Normalize:")
        self.normalize_layout.addWidget(self.normalize_label)
        self.normalize_checkbox = QCheckBox()
        self.normalize_layout.addWidget(self.normalize_checkbox)
        self.boxes_layout.addWidget(self.normalize_widget)

        # region - legend
        self.legend_widget = QWidget()
        self.legend_layout = QHBoxLayout()
        self.legend_widget.setLayout(self.legend_layout)
        self.legend_label = QLabel("Legend:")
        self.legend_layout.addWidget(self.legend_label)
        self.legend_checkbox = QCheckBox()
        self.legend_checkbox.setChecked(True)
        self.legend_layout.addWidget(self.legend_checkbox)
        self.boxes_layout.addWidget(self.legend_widget)

        # region - max
        self.optimum_widget = QWidget()
        self.optimum_layout = QHBoxLayout()
        self.optimum_widget.setLayout(self.optimum_layout)
        self.optimum_label = QLabel("Optimum:")
        self.optimum_layout.addWidget(self.optimum_label)
        self.optimum_checkbox = QCheckBox()
        self.optimum_checkbox.setChecked(True)
        self.optimum_layout.addWidget(self.optimum_checkbox)
        self.boxes_layout.addWidget(self.optimum_widget)

        self.layout.addWidget(self.boxes_widget)

        
