import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout,
    QLabel, QMainWindow, QPushButton, QHBoxLayout, QTabBar
)
from PyQt5.QtCore import Qt


class FenetrePrincipale(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QTabWidget avec fermeture + ajout")
        self.setGeometry(300, 200, 600, 400)

        self.compteur_onglets = 1

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        # QTabWidget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.fermer_onglet)
        self.tabs.setMovable(True)
        self.layout.addWidget(self.tabs)

        # Ajouter le premier onglet
        self.ajouter_onglet()

        # Créer un bouton "Ajouter un onglet" et l'intégrer comme onglet
        self.bouton_ajouter = QPushButton("➕")
        self.bouton_ajouter.setFixedWidth(40)
        self.bouton_ajouter.clicked.connect(self.ajouter_onglet)

        # Onglet factice pour le bouton "ajouter"
        self.onglet_factice = QWidget()
        self.tabs.addTab(self.onglet_factice, "")  # Onglet vide
        self.tabs.tabBar().setTabButton(self.tabs.count() - 1, QTabBar.RightSide, self.bouton_ajouter)

        # Empêcher la fermeture du bouton d'ajout
        self.tabs.setTabEnabled(self.tabs.count() - 1, False)

    def ajouter_onglet(self):
        nom_onglet = f"Onglet {self.compteur_onglets}"
        contenu = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Contenu de {nom_onglet}"))
        contenu.setLayout(layout)

        # Insérer le nouvel onglet juste avant le bouton "➕"
        index = self.tabs.count() - 1
        self.tabs.insertTab(index, contenu, nom_onglet)
        self.tabs.setCurrentIndex(index)

        self.compteur_onglets += 1

    def fermer_onglet(self, index):
        if self.tabs.count() <= 2:  # 1 onglet + 1 bouton "ajouter"
            return  # Ne pas fermer s'il ne reste qu'un onglet réel
        self.tabs.removeTab(index)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    fenetre = FenetrePrincipale()
    fenetre.show()
    sys.exit(app.exec_())
