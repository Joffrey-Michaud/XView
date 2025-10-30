from PyQt5.QtWidgets import QFileDialog, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QComboBox, QLabel, QSizePolicy, QSpacerItem, QLineEdit, QMessageBox, QCheckBox
from PyQt5.QtCore import QDir, Qt
from xview import get_config_file, set_config_data, get_config_data
from xview.settings.section import Section
from xview.remote.remote_utils import get_remote_configs, get_remote_config_names, del_remote_config, change_exp_folder, change_host_name, change_login, change_remote_name, change_enabled_status
from xview.remote.add_remote_window import AddRemoteWindow


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
                                      "- Host name: The IP address or domain name of the remote server.\n"
                                      "- User name: Your username on the remote server.\n"
                                      "- The experiment folder path on the remote server.\n\n"
                                      "Once you have this information, click the 'Add Remote' button below to proceed.\n\n"
                                      "Please ensure that you have configured SSH key-based authentication."
                                      )
        self.add_indications.setWordWrap(True)
        self.add_layout.addWidget(self.add_indications)
        self.add_button = QPushButton('Add Remote', self)
        self.add_button.setFixedSize(200, 30)
        self.add_button.clicked.connect(self.open_add_remote_dialog)
        self.add_layout.addWidget(self.add_button)

        self.add_separator()

        # region - Existing remotes
        # --------------------------------------------------------------------------- Existing remotes
        self.existing_section = Section("Existing remotes")
        self.main_layout.addWidget(self.existing_section)

        self.combo_box_remotes = QComboBox()
        # lister les remote existants et les afficher dans un combo box
        self.combo_box_remotes.addItems(get_remote_config_names())
        self.existing_section.add_widget(self.combo_box_remotes)

        self.remote_display = RemoteDisplay(self.combo_box_remotes.currentText(), parent=self)
        self.existing_section.add_widget(self.remote_display)

    def add_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(separator)

    def open_add_remote_dialog(self):
        print("opening dialog window")
        dlg = AddRemoteWindow(self)
        dlg.exec_()  # ouvre la boîte en modal (bloque jusqu’à fermeture)
        # mettre à jour la combo box des remotes
        self.combo_box_remotes.clear()
        self.combo_box_remotes.addItems(get_remote_config_names())
        self.remote_display.init_ui(self.combo_box_remotes.currentText())


class RemoteDisplay(QWidget):
    def __init__(self, remote_name, parent=None):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self.setContentsMargins(0, 0, 0, 0)
        self.parent = parent

        self.remote_name = remote_name

        self.init_ui(remote_name)

    def init_ui(self, remote_name):
        # clear layout
        for i in reversed(range(self.main_layout.count())):
            self.main_layout.itemAt(i).widget().setParent(None)

        self.remote_name = remote_name
        if self.remote_name == "":
            self.main_layout.addWidget(QLabel("No remote configuration available."))
            return

        # --------------------------------------------------- REMOTE NAME
        remote_name_widget = QWidget()
        remote_name_layout = QHBoxLayout()
        remote_name_layout.setContentsMargins(0, 0, 0, 0)
        remote_name_widget.setLayout(remote_name_layout)

        remote_name_layout.addWidget(QLabel(f"Remote name:"))
        remote_name_input = QLineEdit()
        remote_name_input.setText(remote_name)
        remote_name_save_button = QPushButton("Save")
        remote_name_save_button.setFixedSize(100, 25)
        remote_name_save_button.clicked.connect(lambda: self.change_remote_name(remote_name_input.text()))

        remote_name_layout.addWidget(remote_name_input)
        remote_name_layout.addWidget(remote_name_save_button)

        # --------------------------------------------------- HOST NAME
        host_name_widget = QWidget()
        host_name_layout = QHBoxLayout()
        host_name_layout.setContentsMargins(0, 0, 0, 0)
        host_name_widget.setLayout(host_name_layout)

        host_name_layout.addWidget(QLabel(f"Host name:"))
        host_name_input = QLineEdit()
        host_name_input.setText(get_remote_configs()[remote_name]["host_name"])
        host_name_save_button = QPushButton("Save")
        host_name_save_button.setFixedSize(100, 25)
        host_name_save_button.clicked.connect(lambda: self.change_host_name(host_name_input.text()))

        host_name_layout.addWidget(host_name_input)
        host_name_layout.addWidget(host_name_save_button)

        # --------------------------------------------------- USER NAME
        user_name_widget = QWidget()
        user_name_layout = QHBoxLayout()
        user_name_layout.setContentsMargins(0, 0, 0, 0)
        user_name_widget.setLayout(user_name_layout)

        user_name_layout.addWidget(QLabel(f"User name:"))
        user_name_input = QLineEdit()
        user_name_input.setText(get_remote_configs()[remote_name]["login"])
        user_name_save_button = QPushButton("Save")
        user_name_save_button.setFixedSize(100, 25)
        user_name_save_button.clicked.connect(lambda: self.change_login(user_name_input.text()))

        user_name_layout.addWidget(user_name_input)
        user_name_layout.addWidget(user_name_save_button)

        # --------------------------------------------------- EXP FOLDER
        exp_folder_widget = QWidget()
        exp_folder_layout = QHBoxLayout()
        exp_folder_layout.setContentsMargins(0, 0, 0, 0)
        exp_folder_widget.setLayout(exp_folder_layout)

        exp_folder_layout.addWidget(QLabel(f"Experiment folder:"))
        exp_folder_input = QLineEdit()
        exp_folder_input.setText(get_remote_configs()[remote_name]["exp_folder"])
        exp_folder_save_button = QPushButton("Save")
        exp_folder_save_button.setFixedSize(100, 25)
        exp_folder_save_button.clicked.connect(lambda: self.change_exp_folder(exp_folder_input.text()))

        exp_folder_layout.addWidget(exp_folder_input)
        exp_folder_layout.addWidget(exp_folder_save_button)

        # --------------------------------------------------- ENABLE REMOTE TOGGLE
        enable_remote_widget = QWidget()
        enable_remote_layout = QHBoxLayout()
        enable_remote_layout.setContentsMargins(0, 0, 0, 0)
        enable_remote_widget.setLayout(enable_remote_layout)

        enable_remote_checkbox = QCheckBox("Enable Remote")
        enable_remote_checkbox.setChecked(get_remote_configs()[remote_name]["enabled"])
        enable_remote_checkbox.toggled.connect(lambda checked: self.change_remote_enabled(checked))

        enable_remote_layout.addWidget(enable_remote_checkbox)

        # --------------------------------------------------- DELETE REMOTE BUTTON
        delete_remote_button = QPushButton("Delete Remote Configuration")
        delete_remote_button.setStyleSheet("QPushButton { background-color: red; color: white; }")
        delete_remote_button.clicked.connect(self.delete_remote)

        self.main_layout.addWidget(remote_name_widget)
        self.main_layout.addWidget(host_name_widget)
        self.main_layout.addWidget(user_name_widget)
        self.main_layout.addWidget(exp_folder_widget)
        self.main_layout.addWidget(enable_remote_widget)
        self.main_layout.addWidget(delete_remote_button)

    def change_login(self, new_login):
        change_login(self.remote_name, new_login)
        self.init_ui(self.remote_name)

    def change_host_name(self, new_host_name):
        change_host_name(self.remote_name, new_host_name)
        self.init_ui(self.remote_name)

    def change_exp_folder(self, new_exp_folder):
        change_exp_folder(self.remote_name, new_exp_folder)
        self.init_ui(self.remote_name)

    def change_remote_name(self, new_remote_name):
        change_remote_name(self.remote_name, new_remote_name)
        # mettre à jour la combo box des remotes dans RemoteSettings
        # on veut aussi remettre la combobox sur l item qui vient d etre renommé
        if self.parent is not None:
            index = self.parent.combo_box_remotes.findText(self.remote_name)
            self.parent.combo_box_remotes.setItemText(index, new_remote_name)
            self.parent.combo_box_remotes.setCurrentIndex(index)
        self.remote_name = new_remote_name
        self.init_ui(new_remote_name)

    def change_remote_enabled(self, enabled):
        change_enabled_status(self.remote_name, enabled)
        self.init_ui(self.remote_name)

    def delete_remote(self):
        # boite de dialogue de confirmation
        reply = QMessageBox.question(self, 'Confirmation', 'Are you sure you want to delete this remote configuration?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            del_remote_config(self.remote_name)
            # mettre à jour la combo box des remotes dans RemoteSettings
            if self.parent is not None:
                index = self.parent.combo_box_remotes.findText(self.remote_name)
                self.parent.combo_box_remotes.removeItem(index)
            # afficher le premier élément de la liste
            if self.parent.combo_box_remotes.count() > 0:
                first_remote = self.parent.combo_box_remotes.itemText(0)
                self.parent.combo_box_remotes.setCurrentIndex(0)
                self.init_ui(first_remote)
            else:
                self.init_ui("")
