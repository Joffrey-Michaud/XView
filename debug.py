import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from xview.graph.range_widget import RangeWidget

# Assure-toi d'importer RangeWidget ici ou d'avoir son code juste au-dessus


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Range Widget Test")
        self.setGeometry(100, 100, 400, 200)

        self.range_widget = RangeWidget()
        self.setCentralWidget(self.range_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
