from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QMainWindow, QApplication, QHBoxLayout, QVBoxLayout, QWidget, QSplitter, QLabel, QCheckBox, QScrollArea, QPushButton, QListWidget, QListWidgetItem
from PyQt5.QtGui import QPixmap, QIcon, QPalette, QColor, QCursor
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QSizePolicy
import os
from xview.settings.display import DisplaySettings
from xview.settings.folder import FolderSetting
from xview import get_config_file


class SettingsWindow(QWidget):
    def __init__(self, main_gui, parent=None):
        super().__init__(parent)
        self.main_gui = main_gui
        self.setWindowTitle('Settings')
        self.setGeometry(100, 100, 1200, 600)
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        self.dark_mode_enabled = get_config_file()["dark_mode"]

        self.splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)

        self.settings_widgets = {}

        # region - TREE
        self.list = QListWidget()
        self.list.setFixedWidth(200)
        # self.list.setColumnCount(1)
        self.list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.list.setStyleSheet("QTreeWidget::item { padding: 5px; }")
        self.list.itemClicked.connect(self.on_item_clicked)

        self.splitter.addWidget(self.list)

        # region - SETTINGS WIDGET
        self.setting_widget_container = QWidget()
        self.setting_layout = QVBoxLayout()
        self.setting_widget_container.setLayout(self.setting_layout)
        self.splitter.addWidget(self.setting_widget_container)

        self.current_widget = None

        DISPLAY_LABEL = QLabel("DISPLAY SETTINGS")
        self.add_list_entry("Display", widget=DisplaySettings(self))
        self.add_list_entry("Folder", widget=FolderSetting())
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
