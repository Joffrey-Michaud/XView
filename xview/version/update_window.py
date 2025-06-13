from PyQt5.QtWidgets import QDialog, QWidget, QMainWindow, QHBoxLayout, QLabel, QVBoxLayout, QPushButton, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QIcon
import sys
import os
import subprocess
from xview import get_config_file, set_config_file, set_config_data
from datetime import datetime, timedelta


def pull_latest_changes():
    """Effectue un git pull pour récupérer les dernières modifications."""
    try:
        REPO_DIR = os.path.dirname(os.path.abspath(__file__))
        subprocess.run(["git", "pull"], check=True, cwd=REPO_DIR)
        print("Projet mis à jour avec succès.")
    except subprocess.CalledProcessError:
        print("/!\\ Échec du git pull.")


class UpdateWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Update Warning")
        self.setWindowIcon(QIcon("logo_light.png"))
        self.setGeometry(100, 100, 150, 100)

        # self.central_widget = QWidget()
        # self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.label_1 = QLabel("Your version of XView is not up to date!")
        self.label_1.setAlignment(Qt.AlignCenter)
        self.label_2 = QLabel("Do you want to upgrade it now ?")
        self.label_2.setAlignment(Qt.AlignCenter)

        self.btn_layout = QHBoxLayout()
        self.update_btn = QPushButton("Update now")
        self.no_btn = QPushButton("Remind me later")
        self.update_btn.clicked.connect(self.pull_project)
        self.no_btn.clicked.connect(self.do_nothing)

        self.btn_layout.addWidget(self.update_btn)
        self.btn_layout.addWidget(self.no_btn)

        self.layout.addWidget(self.label_1)
        self.layout.addWidget(self.label_2)
        self.layout.addLayout(self.btn_layout)


        # self.central_widget.setLayout(self.layout)
        self.setLayout(self.layout)

        # afficher la fenêtre au centre de l'écran
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

        self.show()

    def do_nothing(self):
        # remind me later
        set_config_data("remind_me_later_date", datetime.now().isoformat())
        self.close()

    def pull_project(self):
        pull_latest_changes()
        self.close()
        set_config_data("remind_me_later_date", datetime.now().isoformat())
        # set_config_data("first_since_update", True)
        os.execv(sys.executable, [sys.executable] + sys.argv)

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
