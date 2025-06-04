from PyQt5.QtWidgets import QDialog, QWidget, QHBoxLayout, QLabel, QVBoxLayout, QPushButton, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QIcon, QPixmap
import sys
import os
from xview import get_config_file, set_config_file, set_config_data
from datetime import datetime, timedelta


class AboutWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("About XView")
        self.setWindowIcon(QIcon("logo_light.png"))
        self.setGeometry(100, 100, 400, 150)

        # self.central_widget = QWidget()
        # self.setCentralWidget(self.central_widget)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.logo_label = QLabel()
        # fixer la taille du label pour le logo
        self.logo_label.setFixedSize(100, 100)
        pixmap = QPixmap('xview/logo_light.png')  # Replace with your logo path
        pixmap = pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.logo_label)

        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout()
        self.right_widget.setLayout(self.right_layout)
        self.layout.addWidget(self.right_widget)

        self.version_label = QLabel(f"Version : {get_config_file()['version']}")
        self.right_layout.addWidget(self.version_label)

        self.git_label = QLabel()
        self.git_label.setText('You can report a bug, suggest a feature, or contribute via the <a href="https://github.com/Joffrey-Michaud/XView" style="color:#1e90ff; text-decoration:none;">project\'s GitHub page</a>.'
                                )
        self.git_label.setOpenExternalLinks(True)
        self.git_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.git_label.setWordWrap(True)

        self.right_layout.addWidget(self.git_label)

        screen = self.screen()
        screen_geometry = screen.geometry()
        window_geometry = self.geometry()
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        self.setGeometry(x, y, window_geometry.width(), window_geometry.height())

        # Set the dark mode palette
        if get_config_file()["dark_mode"] == True:
            self.set_dark_mode()
            self.setWindowIcon(QIcon("logo_dark.png"))
        else:
            self.set_light_mode()
        # self.show()

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
