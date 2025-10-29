from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt
from xview import get_config_file


class Section(QWidget):
    def __init__(self, title, parent=None):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        # si get_config_file()["dark_mode"]: on écrit en blanc, sinon en noir
        self.title_label.setStyleSheet(
            "font-weight: bold; font-size: 16px; color: white;" if get_config_file()["dark_mode"] else "font-weight: bold; font-size: 16px; color: black;"
            )
        # centrer le titre
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container.setLayout(self.container_layout)
        self.layout.addWidget(self.container)

        # ajouter un qspacer dont la place est en dernière
        self.spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.container_layout.addItem(self.spacer)

    def add_widget(self, widget):
        self.container_layout.addWidget(widget)
        # déplacer le spacer à la fin
        self.container_layout.removeItem(self.spacer)
        self.container_layout.addItem(self.spacer)