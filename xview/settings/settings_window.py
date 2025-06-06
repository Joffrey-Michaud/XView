from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QListWidget, QListWidgetItem
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy
from xview.settings.display import DisplaySettings
from xview.settings.preferences import PreferencesSetting
from xview import get_config_file


class SettingsWindow(QWidget):
    def __init__(self, main_gui, parent=None):
        super().__init__(parent)
        self.main_gui = main_gui
        self.setWindowTitle('Settings')
        self.setGeometry(100, 100, 1200, 600)
        self.initUI()

    def initUI(self):
        self.main_layout = QHBoxLayout(self)
        self.setLayout(self.main_layout)

        self.dark_mode_enabled = get_config_file()["dark_mode"]
        self.settings_widgets = {}

        # region - TREE
        self.list = QListWidget()
        self.list.setFixedWidth(100)
        self.list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.list.itemClicked.connect(self.on_item_clicked)

        self.main_layout.addWidget(self.list)

        # region - SETTINGS WIDGET
        self.setting_widget_container = QWidget()
        self.setting_layout = QVBoxLayout()
        self.setting_widget_container.setLayout(self.setting_layout)
        self.main_layout.addWidget(self.setting_widget_container)

        self.current_widget = None

        DISPLAY_LABEL = QLabel("DISPLAY SETTINGS")
        self.add_list_entry("Display", widget=DisplaySettings(self, add_curve_color_callback=self.main_gui.add_curve_color, add_flag_color_callback=self.main_gui.add_flag_color, remove_curve_color_callback=self.main_gui.remove_curve_color, remove_flag_color_callback=self.main_gui.remove_flag_color))
        self.add_list_entry("Preferences", widget=PreferencesSetting())
        # self.add_list_entry("Update")
        # self.add_list_entry("Save")

        self.set_dark_mode(self.dark_mode_enabled)

        self.settings_widgets["Display"].setVisible(True)
        self.current_widget = self.settings_widgets["Display"]

    def add_list_entry(self, label, widget=None):
        item = QListWidgetItem(label)
        self.list.addItem(item)
        self.settings_widgets[label] = widget
        widget.setVisible(False)
        self.setting_layout.addWidget(widget)

    def on_item_clicked(self, item):
        label = item.text()
        if label in self.settings_widgets:
            widget = self.settings_widgets[label]
            if self.current_widget is not None:
                self.current_widget.setVisible(False)
            widget.setVisible(True)
            self.current_widget = widget

    def set_dark_mode(self, dark_mode):
        if dark_mode:
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
            self.dark_mode_enabled = True

            self.setWindowIcon(QIcon("logo_dark.png"))
        else:
            self.setPalette(QApplication.style().standardPalette())
            self.dark_mode_enabled = False
            self.setWindowIcon(QIcon("logo_light.png"))

        self.main_gui.set_dark_mode(dark_mode)
