from PyQt5.QtWidgets import QDialog, QWidget, QMainWindow, QHBoxLayout, QLabel, QVBoxLayout, QPushButton, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QIcon
import sys
import os
from xview import get_config_file, set_config_file, set_config_data
from datetime import datetime, timedelta


class UpdatedNotification(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("XView updated")
        self.setWindowIcon(QIcon("logo_light.png"))
        self.setGeometry(100, 100, 150, 100)

        # self.central_widget = QWidget()
        # self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.label = QLabel("XView has been updated successfully!")
        self.label.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.label)

        self.btn = QPushButton("Close")
        self.btn.clicked.connect(self.close)
        self.layout.addWidget(self.btn)

        self.setLayout(self.layout)

        if get_config_file()["dark_mode"] == True:
            self.set_dark_mode()
            self.setWindowIcon(QIcon("logo_dark.png"))

        # afficher la fenêtre au centre de l'écran
        screen = self.screen()
        screen_geometry = screen.geometry()
        window_geometry = self.geometry()
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        self.setGeometry(x, y, window_geometry.width(), window_geometry.height())

        self.show()

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
