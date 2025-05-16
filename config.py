import sys
from PyQt5.QtWidgets import QApplication, QFileDialog, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from xview.utils.utils import write_json
import os


class FolderSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('XView - Select data folder')
        self.setGeometry(300, 300, 300, 100)

        layout = QVBoxLayout()

        # Create a label to display the logo

        logo_label = QLabel(self)
        pixmap = QPixmap('xview/gui/logo_light.png')  # Replace with your logo path
        if not pixmap.isNull():
            pixmap = pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
        else:
            logo_label.setText("XView")
            logo_label.setStyleSheet("font-size: 24px; font-weight: bold;")
            logo_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(logo_label)
        
        btn = QPushButton('Choose Folder', self)
        btn.clicked.connect(self.save_folder)
        
        layout.addWidget(btn)
        self.setLayout(layout)
        self.show()

    def save_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder_path:
            config = {"data_folder": folder_path}
            os.makedirs(os.path.join("xview", "config"), exist_ok=True)
            write_json(os.path.join("xview", "config", "config.json"), config)

        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FolderSelector()
    sys.exit(app.exec_())