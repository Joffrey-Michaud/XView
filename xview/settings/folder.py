from PyQt5.QtWidgets import QFileDialog, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QDir
from xview import get_config_file, set_config_data


# ------------------------------------------------------------------ SETTINGS DISPLAY
# region - SettingsDisplay
class FolderSetting(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.global_config = get_config_file()
        self.dark_mode_enabled = get_config_file()["dark_mode"]

        self.current_exp_folder = get_config_file()["data_folder"]

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        self.exp_folder_label = QLabel(f"Current exps folder :\n{self.current_exp_folder}")
        self.exp_folder_label.setWordWrap(True)
        # self.exp_folder_label.setStyleSheet("font-size: 15px;")
        self.exp_folder_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.exp_folder_label)

        exp_btn = QPushButton('Choose Exps Folder', self)
        exp_btn.clicked.connect(self.change_exp_folder)
        self.main_layout.addWidget(exp_btn)

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
