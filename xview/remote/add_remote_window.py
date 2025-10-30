"""Fenêtre de dialogue pour ajouter une configuration distante (remote) à XView.

Ce module définit une boîte de dialogue PyQt5 permettant de saisir un nom de remote,
un hôte, un utilisateur et le chemin du dossier d'expériences, puis d'enregistrer
la configuration.
"""
# code for a dialog window to add a remote server in the xview application
from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSizePolicy, QSpacerItem, QPushButton, QApplication
from PyQt5.QtGui import QColor, QIcon, QPalette
from PyQt5.QtCore import Qt
from xview.remote.remote_utils import create_remote_config
from xview import get_config_data
import os

# demander à l'utilisateur :
# - remote name
# - host name
# - user name
# - experiment folder path


class AddRemoteWindow(QDialog):
    """Boîte de dialogue pour créer et enregistrer une configuration distante.

    Saisie: nom du remote, hôte, utilisateur et dossier d'expériences.
    """

    def __init__(self, parent: QWidget = None):
        """Initialise la fenêtre et construit l'interface.

        Args:
            parent: Widget parent optionnel.
        """
        super().__init__(parent)
        self.setWindowTitle("Add Remote Configuration")
        self.setModal(True)
        self.setFixedSize(300, 300)
        # Further implementation would go here to create the dialog UI

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # region - REMOTE NAME
        # -------------------------------------------------------------
        self.remote_name_widget = QWidget()
        remote_name_layout = QHBoxLayout()
        self.remote_name_widget.setLayout(remote_name_layout)

        remote_name_label = QLabel("Remote Name:")
        self.remote_name_input = QLineEdit()
        self.remote_name_input.setPlaceholderText("e.g., cluster-a")
        remote_name_layout.addWidget(remote_name_label)
        remote_name_layout.addWidget(self.remote_name_input)

        remote_name_spacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
        remote_name_layout.addItem(remote_name_spacer)

        self.main_layout.addWidget(self.remote_name_widget)

        # region - HOST NAME
        # -------------------------------------------------------------
        self.host_name_widget = QWidget()
        host_name_layout = QHBoxLayout()
        self.host_name_widget.setLayout(host_name_layout)

        host_name_label = QLabel("Host Name:")
        self.host_name_input = QLineEdit()
        self.host_name_input.setPlaceholderText("e.g., 192.168.1.1")
        host_name_layout.addWidget(host_name_label)
        host_name_layout.addWidget(self.host_name_input)

        host_name_spacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
        host_name_layout.addItem(host_name_spacer)

        self.main_layout.addWidget(self.host_name_widget)

        # region - USER NAME
        # -------------------------------------------------------------
        self.user_name_widget = QWidget()
        user_name_layout = QHBoxLayout()
        self.user_name_widget.setLayout(user_name_layout)

        user_name_label = QLabel("User Name:")
        self.user_name_input = QLineEdit()
        self.user_name_input.setPlaceholderText("e.g., JohnDoe")
        user_name_layout.addWidget(user_name_label)
        user_name_layout.addWidget(self.user_name_input)

        user_name_spacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
        user_name_layout.addItem(user_name_spacer)

        self.main_layout.addWidget(self.user_name_widget)

        # region - EXPERIMENT FOLDER
        # -------------------------------------------------------------
        self.exp_folder_widget = QWidget()
        exp_folder_layout = QHBoxLayout()
        self.exp_folder_widget.setLayout(exp_folder_layout)

        exp_folder_label = QLabel("Experiment Folder:")
        self.exp_folder_input = QLineEdit()
        self.exp_folder_input.setPlaceholderText("e.g., /data/experiments")
        exp_folder_layout.addWidget(exp_folder_label)
        exp_folder_layout.addWidget(self.exp_folder_input)

        exp_folder_spacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
        exp_folder_layout.addItem(exp_folder_spacer)

        self.main_layout.addWidget(self.exp_folder_widget)

        # region - CONFIRM BUTTON
        # -------------------------------------------------------------
        self.confirm_button = QPushButton("Confirm")
        self.main_layout.addWidget(self.confirm_button)
        self.confirm_button.clicked.connect(self.confirm_callback)

        # spacer
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.main_layout.addItem(spacer)

        self.set_dark_mode(get_config_data("dark_mode"))

    def confirm_callback(self):
        """Valide les champs et enregistre la configuration distante.

        Affiche un message d'erreur si un champ est vide, sinon crée la
        configuration et ferme la boîte de dialogue avec accept().
        """
        # check if all fields are filled
        if (not self.remote_name_input.text() or
                not self.host_name_input.text() or
                not self.user_name_input.text() or
                not self.exp_folder_input.text()):
            # show error message
            error_dialog = QDialog(self)
            error_dialog.setFixedWidth(200)
            error_dialog.setWindowTitle("Error")
            error_layout = QVBoxLayout()
            error_dialog.setLayout(error_layout)
            error_label = QLabel("All fields must be filled.")
            error_layout.addWidget(error_label)
            ok_button = QPushButton("OK")
            error_layout.addWidget(ok_button)
            ok_button.clicked.connect(error_dialog.accept)

            # dark mode
            if get_config_data("dark_mode"):
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

                error_dialog.setPalette(dark_palette)

            error_dialog.exec_()
            return

        # If all fields are filled, proceed with the confirmation
        remote_name = self.remote_name_input.text()
        host_name = self.host_name_input.text()
        user_name = self.user_name_input.text()
        exp_folder = self.exp_folder_input.text()

        # Here you can add the code to handle the confirmed values
        create_remote_config(remote_name, host_name, user_name, exp_folder)
        self.accept()

    def set_dark_mode(self, dark_mode):
        """Applique le thème sombre ou clair à la fenêtre.

        Args:
            dark_mode: True pour activer le mode sombre, False pour le désactiver.
        """
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
