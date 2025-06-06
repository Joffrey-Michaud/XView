from PyQt5.QtWidgets import QScrollArea, QApplication, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QCheckBox, QSpacerItem
from PyQt5.QtGui import QIcon, QPalette, QColor, QCursor
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QSizePolicy
import os


class CurvesSelector(QWidget):
    def __init__(self, parent=None,
                 #  curves_list=None, flags_list=None
                 ):
        super().__init__()
        self.dark_mode_enabled = False
        self.initUI()
        self.setMinimumHeight(100)
        self.setMaximumHeight(400)

    def initUI(self):
        self.setWindowTitle('Curves Selector')

        self.boxes = {}
        self.current_path = ""

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        label = QLabel("Select curves to display")
        label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(label)

        self.scroll_area = QScrollArea()

        self.scroll_area.setWidgetResizable(True)

        self.boxes_container = QWidget()
        self.boxes_container_layout = QVBoxLayout()
        self.boxes_container.setLayout(self.boxes_container_layout)

        self.scroll_area.setWidget(self.boxes_container)
        self.main_layout.addWidget(self.scroll_area)

        self.spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.boxes_container_layout.addItem(self.spacer)

    def reset_window(self, path=None):
        if path != self.current_path:
            # ...
            # supprimer les boxes
            if self.boxes != {}:
                for k, (_, container) in self.boxes.items():
                    self.boxes_container_layout.removeWidget(container)
                    container.deleteLater()
                self.boxes = {}
            self.current_path = path

    def init_boxes(self, curves_list=None, flags_list=None, path=None):
        if curves_list is not None:
            for curve_name in curves_list:
                self.add_line_box(curve_name)
                self.add_line_box(f"{curve_name} (MA)")

            for flag in flags_list:
                self.add_line_box(flag)

    def update_boxes(self, curves_list=None, flags_list=None):
        if curves_list is not None:
            for curve_name in curves_list:
                if curve_name not in self.boxes:
                    self.add_line_box(curve_name)
                    self.add_line_box(f"{curve_name} (MA)")

        if flags_list is not None:
            for flag in flags_list:
                if flag not in self.boxes:
                    self.add_line_box(flag)

    def add_line_box(self, curve_name):
        container = QWidget()
        h_layout = QHBoxLayout()
        h_layout.setSpacing(10)
        h_layout.setContentsMargins(0, 0, 0, 0)

        checkbox = QCheckBox()  # ajouter une checkbox cochée
        checkbox.setChecked(True)
        checkbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        label = QLabel(curve_name)
        label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        label.setAlignment(Qt.AlignVCenter)

        h_layout.addWidget(checkbox)
        h_layout.addWidget(label)

        container.setLayout(h_layout)

        self.boxes_container_layout.insertWidget(self.boxes_container_layout.count() - 1, container)
        self.boxes[curve_name] = (checkbox, container)

    def toggle_dark_mode(self):
        if not self.dark_mode_enabled:
            self.dark_mode_enabled = True
            self.set_dark_mode()
            self.setWindowIcon(QIcon("logo_dark.png"))
        else:
            self.dark_mode_enabled = False
            self.set_light_mode()
            self.setWindowIcon(QIcon("logo_light.png"))
        # self.display_model_image()

    def set_dark_mode(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        self.setPalette(dark_palette)

    def set_light_mode(self):
        self.setPalette(QApplication.style().standardPalette())

    def move_to_cursor_bottom_left(self):
        mouse_pos = QCursor.pos()
        window_size = self.size()
        new_pos = QPoint(mouse_pos.x(), mouse_pos.y() - window_size.height())
        self.move(new_pos)
