from PyQt5.QtWidgets import QFileDialog, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QComboBox, QLabel, QSizePolicy, QSpacerItem, QLineEdit
from PyQt5.QtCore import QDir, Qt
from xview import get_config_file, set_config_data, get_config_data
from xview.settings.section import Section
from xview.remote.remote_utils import create_remote_config, get_all_remote_configs, del_remote_config


# ------------------------------------------------------------------ REMOTE SETTINGS
# region - RemoteSettings
class RemoteSettings(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.global_config = get_config_file()
        self.dark_mode_enabled = get_config_file()["dark_mode"]

        self.current_exp_folder = get_config_file()["data_folder"]

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        # region - Add remote
        # --------------------------------------------------------------------------- Add remote
        self.add_section = Section("Add remote")
        self.main_layout.addWidget(self.add_section)

        self.add_widget = QWidget()
        self.add_layout = QVBoxLayout()
        self.add_layout.setContentsMargins(0, 0, 0, 0)
        self.add_widget.setLayout(self.add_layout)
        self.add_section.add_widget(self.add_widget)

        self.add_indications = QLabel("To add a new remote configuration, you'll need the following informations:\n\n"
                                      "- Remote Name: A friendly name for the remote configuration.\n"
                                      "- Host: The IP address or domain name of the remote server.\n"
                                      "- Username: Your username on the remote server.\n"
                                      "- The experiment folder path on the remote server.\n\n"
                                      "Once you have this information, click the 'Add Remote' button below to proceed.\n\n"
                                      "Please ensure that you have configured SSH key-based authentication."
                                      )
        self.add_indications.setWordWrap(True)
        self.add_layout.addWidget(self.add_indications)
        self.add_button = QPushButton('Add Remote', self)
        self.add_button.setFixedSize(200, 30)
        # self.add_button.clicked.connect(self.parent.open_add_remote_dialog)
        self.add_layout.addWidget(self.add_button)

        self.add_separator()

        # region - Existing remotes
        # --------------------------------------------------------------------------- Existing remotes
        self.existing_section = Section("Existing remotes")
        self.main_layout.addWidget(self.existing_section)

        


    def add_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(separator)