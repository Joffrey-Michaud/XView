from PyQt5.QtWidgets import QDialog, QWidget, QMainWindow, QHBoxLayout, QLabel, QVBoxLayout, QPushButton, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QIcon
from xview.update.update_project import pull_latest_changes
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

        self.show()

