from PyQt5.QtWidgets import QApplication
from xview.version.update_window import UpdateWindow
import sys


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    ex = UpdateWindow()
    sys.exit(app.exec_())