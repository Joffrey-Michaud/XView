"""Placeholder for trash folder settings UI (capacity/timer)."""

from PyQt5.QtWidgets import QFileDialog, QWidget, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QDir
from xview import get_config_file, set_config_data


# ------------------------------------------------------------------ SETTINGS TRASH FOLDER
# region - TrashFolderSettings
class TrashFolderSettings(QWidget):
    """UI to configure trash capacity and retention (not fully implemented)."""

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.global_config = get_config_file()
        self.dark_mode_enabled = get_config_file()["dark_mode"]

        self.current_trash_capacity = get_config_file()["trash_capacity"]
        self.current_trash_timer = get_config_file()["trash_timer"]

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        trash_capacity_layout = QHBoxLayout()
        self.trash_capacity_input = QLabel(f"{self.current_trash_capacity} Go")

        self.trash_capacity = QLabel(f"Set trash capacity (Go):")
        self.trash_capacity.setWordWrap(True)
        # self.trash_capacity.setStyleSheet("font-size: 15px;")
        self.trash_capacity.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.trash_capacity)

        self.trash_timer = QLabel(f"Set trash timer (days):")
        self.trash_timer.setWordWrap(True)
        # self.trash_timer.setStyleSheet("font-size: 15px;")
        self.trash_timer.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.trash_timer)

        exp_btn = QPushButton('Choose Exps Folder', self)
        exp_btn.clicked.connect(self.change_exp_folder)
        self.main_layout.addWidget(exp_btn)

    def change_exp_folder(self):
        """Open a directory picker and store the selected experiments path."""

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
