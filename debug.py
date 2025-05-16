import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QColorDialog, QHBoxLayout, QVBoxLayout
)
from PyQt5.QtGui import QColor

class ColorPickerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sélecteur de couleurs")

        self.color_buttons = []
        self.init_ui()

    def init_ui(self):
        # Couleurs de base
        base_colors = [
            QColor("#FF0000"),  # Rouge
            QColor("#00FF00"),  # Vert
            QColor("#0000FF"),  # Bleu
            QColor("#FFFF00"),  # Jaune
            QColor("#FF00FF")   # Magenta
        ]

        color_layout = QHBoxLayout()
        for color in base_colors:
            btn = QPushButton()
            btn.setFixedSize(50, 50)
            btn.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
            btn.clicked.connect(self.open_color_dialog)
            self.color_buttons.append(btn)
            color_layout.addWidget(btn)

        # Bouton Terminer
        finish_button = QPushButton("Terminer")
        finish_button.clicked.connect(self.terminate)

        main_layout = QVBoxLayout()
        main_layout.addLayout(color_layout)
        main_layout.addWidget(finish_button)

        self.setLayout(main_layout)

    def open_color_dialog(self):
        sender = self.sender()
        current_color = sender.palette().button().color()

        color = QColorDialog.getColor(initial=current_color, parent=self)

        if color.isValid():
            sender.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")

    def terminate(self):
        print("Couleurs sélectionnées :")
        for i, btn in enumerate(self.color_buttons, 1):
            color = btn.palette().button().color()
            print(f"Couleur {i}: {color.name()}")
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ColorPickerWidget()
    window.show()
    sys.exit(app.exec_())
