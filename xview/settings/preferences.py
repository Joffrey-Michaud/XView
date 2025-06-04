import sys
from PyQt5.QtWidgets import QFileDialog, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QComboBox, QLabel, QSizePolicy, QSpacerItem
# from PyQt5.QtGui import QPixmap, QIcon, QPalette, QColor
from PyQt5.QtCore import Qt, QDir
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.figure import Figure
# from xview.utils.utils import write_json, read_json, compute_moving_average
# import os
import numpy as np
# import time
# from xview.version.update_project import warn_if_outdated
from xview import get_config_file, set_config_file, set_config_data, config_exists


# ------------------------------------------------------------------ SETTINGS DISPLAY
# region - PreferencesSetting
class PreferencesSetting(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.global_config = get_config_file()
        self.dark_mode_enabled = get_config_file()["dark_mode"]

        self.current_exp_folder = get_config_file()["data_folder"]

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        # region - Folder Selection
        # --------------------------------------------------------------------------- Folder Selection
        self.folder_widget = QWidget()
        self.folder_layout = QHBoxLayout()
        self.folder_widget.setLayout(self.folder_layout)
        self.main_layout.addWidget(self.folder_widget)

        exp_btn = QPushButton('Choose Exp. Folder', self)
        # taille du bouton fixée
        exp_btn.setFixedSize(200, 20)
        exp_btn.clicked.connect(self.change_exp_folder)
        self.folder_layout.addWidget(exp_btn)

        self.exp_folder_label = QLabel(f"Current exps folder : {self.current_exp_folder}")
        self.exp_folder_label.setWordWrap(True)
        # self.exp_folder_label.setStyleSheet("font-size: 15px;")
        # self.exp_folder_label.setAlignment(Qt.AlignCenter)
        self.folder_layout.addWidget(self.exp_folder_label)

        self.add_separator()

        # region - Auto Update
        # --------------------------------------------------------------------------- Auto Update
        self.auto_upd_widget = QWidget()
        self.auto_upd_layout = QHBoxLayout()
        self.auto_upd_widget.setLayout(self.auto_upd_layout)
        self.main_layout.addWidget(self.auto_upd_widget)

        auto_upd_label = QLabel("Enabling Auto Update :")
        auto_upd_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.auto_upd_layout.addWidget(auto_upd_label)
        self.auto_upd_combo = QComboBox()
        self.auto_upd_combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.auto_upd_combo.setFixedSize(100, 20)
        self.auto_upd_combo.addItems(["Enabled", "Disabled"])
        self.auto_upd_combo.setCurrentText("Enabled" if self.global_config["auto_update"] else "Disabled")
        self.auto_upd_combo.currentTextChanged.connect(self.change_auto_update)
        self.auto_upd_layout.addWidget(self.auto_upd_combo)

        self.auto_upd_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # self.auto_upd_layout.setContentsMargins(0, 0, 0, 0)
        # self.auto_upd_layout.setSpacing(0)  # Ajuste à ta convenance

        self.add_separator()

        self.main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def change_exp_folder(self):

        dialog = QFileDialog(self, 'Select Folder')
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOptions(QFileDialog.ShowDirsOnly | QFileDialog.DontUseNativeDialog)
        dialog.setFilter(dialog.filter() | QDir.Hidden)

        if dialog.exec_():
            folder_path = dialog.selectedFiles()[0]
        else:
            folder_path = None

        if folder_path:
            self.current_exp_folder = folder_path
            self.exp_folder_label.setText(f"Current exps folder :\n{self.current_exp_folder}")
            set_config_data('data_folder', folder_path)

    def change_auto_update(self, text):
        if text == "Enabled":
            set_config_data('auto_update', True)
        else:
            set_config_data('auto_update', False)
        self.global_config = get_config_file()

    def add_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(separator)
