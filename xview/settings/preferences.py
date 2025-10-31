"""Preferences panel for general settings such as folders and auto-update."""

from PyQt5.QtWidgets import QFileDialog, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QComboBox, QLabel, QSizePolicy, QSpacerItem, QLineEdit
from PyQt5.QtCore import QDir, Qt
from xview import get_config_file, set_config_data, get_config_data
from xview.settings.section import Section


# ------------------------------------------------------------------ SETTINGS DISPLAY
# region - PreferencesSetting
class PreferencesSetting(QWidget):
    """General application preferences section."""

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
        self.folder_section = Section("Experiment Folder")
        self.main_layout.addWidget(self.folder_section)

        self.folder_widget = QWidget()
        self.folder_layout = QHBoxLayout()
        self.folder_layout.setContentsMargins(0, 0, 0, 0)
        self.folder_widget.setLayout(self.folder_layout)

        exp_btn = QPushButton('Choose Exp. Folder', self)
        # taille du bouton fixée
        exp_btn.setFixedSize(200, 20)
        exp_btn.clicked.connect(self.change_exp_folder)
        self.folder_layout.addWidget(exp_btn)

        self.exp_folder_label = QLabel(f"Current exps folder : {self.current_exp_folder}")
        self.exp_folder_label.setWordWrap(True)
        self.folder_layout.addWidget(self.exp_folder_label)

        self.folder_section.add_widget(self.folder_widget)

        self.add_separator()

        # region - Auto Update
        # --------------------------------------------------------------------------- Auto Update
        self.auto_upd_section = Section("Auto Update")
        self.main_layout.addWidget(self.auto_upd_section)

        self.auto_upd_widget = QWidget()
        self.auto_upd_layout = QHBoxLayout()
        self.auto_upd_layout.setContentsMargins(0, 0, 0, 0)
        self.auto_upd_widget.setLayout(self.auto_upd_layout)
        self.auto_upd_section.add_widget(self.auto_upd_widget)

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

        # region - TRASH FOLDER SETTINGS
        # --------------------------------------------------------------------------- TRASH FOLDER SETTINGS
        self.trash_section = Section("Trash Parameters")
        self.main_layout.addWidget(self.trash_section)
        # self.trash_widget = QWidget()
        # self.trash_layout = QVBoxLayout()
        # self.trash_widget.setLayout(self.trash_layout)
        # # enlever les marges du trash layout
        # self.trash_layout.setContentsMargins(0, 0, 0, 0)

        # ------------------------------------------ TRASH SIZE SETTINGS
        self.trash_size_widget = QWidget()
        self.trash_size_layout = QHBoxLayout()
        self.trash_size_layout.setContentsMargins(0, 0, 0, 0)
        self.trash_size_widget.setLayout(self.trash_size_layout)
        self.trash_section.add_widget(self.trash_size_widget)

        trash_size_label = QLabel("Set trash max size (Go) :")
        trash_size_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.trash_size_layout.addWidget(trash_size_label)

        self.trash_size_input = QLineEdit()
        self.trash_size_input.setPlaceholderText(f"{get_config_data('trash_max_size')}")
        self.trash_size_input.editingFinished.connect(self.update_trash_size)
        self.trash_size_input.setFixedWidth(100)
        self.trash_size_layout.addWidget(self.trash_size_input)

        desc_label = QLabel("(0 means no limit)")
        desc_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.trash_size_layout.addWidget(desc_label)
        self.trash_size_layout.addItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))  # to the left

        # ------------------------------------------ TRASH DAYS SETTINGS
        self.trash_days_widget = QWidget()
        self.trash_days_layout = QHBoxLayout()
        self.trash_days_layout.setContentsMargins(0, 0, 0, 0)
        self.trash_days_widget.setLayout(self.trash_days_layout)
        self.trash_section.add_widget(self.trash_days_widget)

        trash_days_label = QLabel("Set trash max days (days) :")
        trash_days_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.trash_days_layout.addWidget(trash_days_label)

        self.trash_days_input = QLineEdit()
        self.trash_days_input.setPlaceholderText(f"{get_config_data('trash_max_days')}")
        self.trash_days_input.editingFinished.connect(self.update_trash_days)
        self.trash_days_input.setFixedWidth(100)
        self.trash_days_layout.addWidget(self.trash_days_input)

        self.trash_days_layout.addWidget(QLabel("(0 means no limit)"))
        self.trash_days_layout.addItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))  # to the left

        # self.trash_section.add_widget(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def change_exp_folder(self):
        """Open a folder dialog and save the chosen experiments directory."""

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
        """Enable or disable auto-update based on combo selection."""
        if text == "Enabled":
            set_config_data('auto_update', True)
        else:
            set_config_data('auto_update', False)
        self.global_config = get_config_file()

    def add_separator(self):
        """Insert a horizontal separator line in the layout."""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(separator)

    def update_trash_size(self):
        """Persist the maximum trash size (GB); 0 means unlimited."""
        size = float(self.trash_size_input.text())
        set_config_data('trash_max_size', size)

    def update_trash_days(self):
        """Persist the maximum trash retention (days); 0 means unlimited."""
        days = int(self.trash_days_input.text())
        set_config_data('trash_max_days', days)
