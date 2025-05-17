import sys
from PyQt5.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

# class MainWindow(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Liste avec sous-items")
#         self.setGeometry(100, 100, 300, 300)

#         layout = QVBoxLayout()

#         # Création du QTreeWidget
#         self.tree = QTreeWidget()
#         # self.tree.setHeaderLabel("Éléments")
#         self.tree.setHeaderHidden(True)

#         # Connexion du signal
#         self.tree.itemClicked.connect(self.handle_item_clicked)

#         # Éléments principaux
#         item_a = QTreeWidgetItem(["A"])
#         item_b = QTreeWidgetItem(["B"])
#         item_c = QTreeWidgetItem(["C"])

#         # Sous-éléments de B
#         item_b1 = QTreeWidgetItem(["B1"])
#         item_b2 = QTreeWidgetItem(["B2"])
#         item_b.addChildren([item_b1, item_b2])

#         # Ajouter les éléments principaux
#         self.tree.addTopLevelItems([item_a, item_b, item_c])

#         layout.addWidget(self.tree)
#         self.setLayout(layout)

#     def handle_item_clicked(self, item, column):
#         # Vérifie si l'item a des enfants
#         if item.childCount() == 0:
#             print(f"Item cliqué : {item.text(0)}")

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())

from xview.experiment import Experiment
import numpy as np


my_exp = Experiment("exp_3", infos={"chat": "gris", "gourmand": "énormément"},
                    group="test_groups"
                    )

my_exp.set_train_status()

# A1, A2 = 0.85, 0.96

A1,A2 = np.random.rand(2)

def sinusoid(x, A):
    return A * np.sin(x)

# points = np.linspace(0, 2 * np.pi, 200)
# amplitudes = [1, 2, 0.5, 1.5, 0.8]
# for i, (color, amp) in enumerate(zip(curves_colors, amplitudes)):
#     y = amp * np.sin(x + i)

points = np.linspace(0, 2 * np.pi, 200)

for i, x in enumerate(points):
    y1 = A1 * np.sin(x + 1)
    y2 = A2 * np.sin(x + 2)
    my_exp.add_score(name="score_1", x=x, y=y1)
    my_exp.add_score(name="score_2", x=x, y=y2)

    if i in [50, 75, 150]:
        my_exp.add_flag(name="flag_1", x=x)

my_exp.set_finished_status()


# import sys
# from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
# from xview.tree_widget import MyTreeWidget  # ou copier la classe directement ici

# def coucou(item):
#         print(f"Item cliqué : {item.text(0)}")

# class MainWindow(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Liste dynamique")
#         self.setGeometry(100, 100, 300, 300)

#         layout = QVBoxLayout()

#         data = [
#             "A",
#             {"B": ["B1", "B2"]},
#             "C",
#             {"D": ["D1", "D2", "D3"]},
#             "E"
#         ]

#         tree_widget = MyTreeWidget(items=data, on_click_callback=coucou)
#         layout.addWidget(tree_widget)

#         self.setLayout(layout)

# if __name__ == "__main__":

    

#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())
