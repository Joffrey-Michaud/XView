import os
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QListWidget, QWidget, QHBoxLayout,
                             QCheckBox, QLabel, QGridLayout, QPushButton, QSplitter, QTextEdit, QLineEdit, QTableWidget, QTableWidgetItem)
from PyQt5.QtGui import QPixmap, QImage, QBrush, QColor, QFont, QIcon, QPalette
from PyQt5.QtCore import QTimer, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from xview.utils.utils import read_file, read_json, compute_moving_average, write_file, write_json
from xview.tree_widget import MyTreeWidget
from config import ConfigManager


class ExperimentViewer(QMainWindow):
    def __init__(self, config_file_path):
        super().__init__()
        self.config_file_path = config_file_path

        self.experiments_dir = read_json(config_file_path)["data_folder"]
        self.current_experiment_name = None

        self.dark_mode_enabled = False
        
        self.model_image_file = None

        # Configurer l'interface principale
        self.setWindowTitle("XView")
        self.setWindowIcon(QIcon("logo_light.png"))
        self.setGeometry(100, 100, 1200, 800)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Layout principal avec QSplitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(splitter)

        # Widget gauche : Contrôles et listes des expériences
        left_widget = QWidget()
        left_layout = QGridLayout()
        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)

        # Boutons Refresh (en colonne)
        self.refresh_graph_button = QPushButton("Refresh Graph")
        self.refresh_graph_button.clicked.connect(self.refresh_graph)
        left_layout.addWidget(self.refresh_graph_button, 0, 0)

        self.refresh_experiments_button = QPushButton("Refresh Experiments")
        self.refresh_experiments_button.clicked.connect(self.update_experiment_list)
        left_layout.addWidget(self.refresh_experiments_button, 1, 0)

        # Bouton Save Graph et Finish exp
        save_finish_widget = QWidget()
        save_finish_layout = QHBoxLayout()
        save_finish_layout.setContentsMargins(0, 0, 0, 0)
        save_finish_widget.setLayout(save_finish_layout)

        self.save_graph_button = QPushButton("Save Graph")
        self.save_graph_button.clicked.connect(self.save_graph)
        save_finish_layout.addWidget(self.save_graph_button)

        self.finish_exp_button = QPushButton("Finish Exp.")
        self.finish_exp_button.clicked.connect(self.finish_experiment)
        save_finish_layout.addWidget(self.finish_exp_button)

        left_layout.addWidget(save_finish_widget, 2, 0)

        # Bouton dark mode et config panel
        dark_config_widget = QWidget()
        dark_config_layout = QHBoxLayout()
        dark_config_layout.setContentsMargins(0, 0, 0, 0)
        dark_config_widget.setLayout(dark_config_layout)

        self.dark_mode_button = QPushButton("Dark mode")
        self.dark_mode_button.clicked.connect(self.toggle_dark_mode)
        dark_config_layout.addWidget(self.dark_mode_button)

        self.config_button = QPushButton("Config panel")
        self.config_button.clicked.connect(self.open_config_panel)
        dark_config_layout.addWidget(self.config_button)

        left_layout.addWidget(dark_config_widget, 3, 0)

        self.config_window = None

        # show infos et dark mode
        # boxes_widget = QWidget()
        # boxes_layout = QGridLayout()
        # boxes_widget.setLayout(boxes_layout)
        # left_layout.addWidget(boxes_widget, 3, 0)

        # Case à cocher pour afficher/masquer le schéma
        # self.show_network_cb = QCheckBox("Show Infos")
        # self.show_network_cb.setChecked(True)
        # self.show_network_cb.stateChanged.connect(self.toggle_model_image)
        # boxes_layout.addWidget(self.show_network_cb, 0, 0)

        # # Case à cocher pour le darkmode
        # self.box_dark_mode = QCheckBox("Dark mode")
        # self.box_dark_mode.setChecked(False)
        # self.box_dark_mode.stateChanged.connect(self.toggle_dark_mode)
        # boxes_layout.addWidget(self.box_dark_mode, 0, 1)

        # Listes des expériences
        # self.training_list = QListWidget()
        # self.finished_list = QListWidget()
        self.training_list = MyTreeWidget(self, display_exp=self.display_experiment)
        self.finished_list = MyTreeWidget(self, display_exp=self.display_experiment)
        left_layout.addWidget(QLabel("Experiments in progress"), 4, 0)
        left_layout.addWidget(self.training_list, 5, 0)
        left_layout.addWidget(QLabel("Finished experiments"), 6, 0)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search for an experiment...")
        # self.search_bar.textChanged.connect(self.filter_experiments)
        self.search_bar.textChanged.connect(self.finished_list.filter_items)
        left_layout.addWidget(self.search_bar, 7, 0)  # Ajout sous le titre "Expériences terminées"

        left_layout.addWidget(self.finished_list, 8, 0)  # Liste des expériences terminées sous la barre de recherche

        # Widget central : Graphique Matplotlib
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        splitter.addWidget(self.canvas)

        # Widget droit : Affichage du schéma du modèle et des informations
        right_widget = QSplitter(Qt.Vertical)
        splitter.addWidget(right_widget)

        # Affichage du schéma du modèle
        self.model_image_label = QLabel()
        self.model_image_label.setMinimumSize(300, 300)
        self.model_image_label.setStyleSheet("border: 1px solid black; background-color: white")
        self.model_image_label.setAlignment(Qt.AlignCenter)
        right_widget.addWidget(self.model_image_label)

        # Affichage des informations du fichier JSON
        self.exp_info_text = QTextEdit()
        self.exp_info_text.setReadOnly(True)
        # right_widget.addWidget(self.exp_info_text)
        self.exp_info_table = QTableWidget()
        self.exp_info_table.setAlternatingRowColors(True)
        self.exp_info_table.setColumnCount(2)  # Deux colonnes : Clé | Valeur
        self.exp_info_table.setHorizontalHeaderLabels(["Param", "Value"])
        self.exp_info_table.horizontalHeader().setStretchLastSection(True)  # Ajuste la largeur de la dernière colonne
        right_widget.addWidget(self.exp_info_table)

        # Configurer les proportions par défaut
        splitter.setStretchFactor(0, 1)  # Zone des contrôles
        splitter.setStretchFactor(1, 4)  # Zone du graphique
        splitter.setStretchFactor(2, 1)  # Zone de l'image et des infos
        right_widget.setStretchFactor(0, 3)  # Zone du schéma
        right_widget.setStretchFactor(1, 2)  # Zone des infos

        # Cases à cocher pour les courbes
        self.show_train_cb = QCheckBox("Display Train Loss")
        self.show_train_cb.setChecked(True)
        self.show_val_cb = QCheckBox("Display Validation Loss")
        self.show_val_cb.setChecked(True)
        self.show_train_ma_cb = QCheckBox("Display Train Loss (MA)")
        self.show_train_ma_cb.setChecked(True)
        self.show_val_ma_cb = QCheckBox("Display Validation Loss (MA)")
        self.show_val_ma_cb.setChecked(True)

        left_layout.addWidget(self.show_train_cb, 9, 0)
        left_layout.addWidget(self.show_val_cb, 10, 0)
        left_layout.addWidget(self.show_train_ma_cb, 11, 0)
        left_layout.addWidget(self.show_val_ma_cb, 12, 0)

        # Connexion des signaux)
        self.show_train_cb.stateChanged.connect(self.update_plot)
        self.show_val_cb.stateChanged.connect(self.update_plot)
        self.show_train_ma_cb.stateChanged.connect(self.update_plot)
        self.show_val_ma_cb.stateChanged.connect(self.update_plot)

        # region - QTIMER
        # Timers pour mise à jour
        self.list_update_timer = QTimer(self)
        self.list_update_timer.timeout.connect(self.update_experiment_list)
        # self.list_update_timer.timeout.connect(self.update_plot)  # Mise à jour du graphique en même temps que les listes
        self.list_update_timer.timeout.connect(self.refresh_graph)  # Mise à jour du graphique en même temps que les listes
        self.list_update_timer.start(self.get_interval())

        # Variables pour le stockage temporaire
        self.current_scores = {}
        self.current_flags = {}
        self.current_train_loss = []
        self.current_val_loss = []

        if not os.path.isfile(os.path.join("xview", "config", "dark_mode.json")):
            write_json(os.path.join("xview", "config", "dark_mode.json"), {"dark_mode": False})
        # self.dark_mode_enabled = self.read_dark_mode_state()
        # print("DARK MODE ENABLED :", self.dark_mode_enabled)
        if self.read_dark_mode_state():
            self.toggle_dark_mode()

        # Mise à jour initiale
        self.update_experiment_list()

    def read_dark_mode_state(self):
        """Lit l'état du mode sombre à partir du fichier JSON."""
        dark_mode_state = read_json(os.path.join("xview", "config", "dark_mode.json"))
        return dark_mode_state["dark_mode"]

    def get_interval(self): 
        interval = read_json(self.config_file_path)["update_interval"]
        return int(interval * 1000)

    def open_config_panel(self):
        if self.config_window is None or not self.config_window.isVisible():
            # self.config_window = ConfigManager(self.config_file_path)
            self.config_window = ConfigManager()
            if self.dark_mode_enabled:
                self.config_window.toggle_dark_mode()
            self.config_window.show()
        else:
            self.config_window.activateWindow()
            if self.dark_mode_enabled:
                self.config_window.toggle_dark_mode()
            self.config_window.raise_()

    def toggle_model_image(self):
        """Affiche ou masque l'image du modèle et les infos en fonction de l'état de la case à cocher."""
        if self.show_network_cb.isChecked():
            self.model_image_label.show()
            self.exp_info_text.show()
        else:
            self.model_image_label.hide()
            self.exp_info_text.hide()

    def filter_experiments(self):
        search_text = self.search_bar.text().lower()
        self.finished_list.clear()
        for exp_name in self.full_experiment_list:
            if search_text in exp_name.lower():
                self.finished_list.addItem(exp_name)

    @staticmethod
    def build_exp_tree(path):
        def build(path):
            training_exps = []
            finished_exps = []

            for entry in os.listdir(path):
                entry_path = os.path.join(path, entry)
                if os.path.isdir(entry_path):
                    status_file = os.path.join(entry_path, "status.txt")
                    if os.path.exists(status_file):
                        status = read_file(status_file, return_str=True)
                        if status == "training" or status == "init":
                            training_exps.append(entry)
                        elif status == "finished":
                            finished_exps.append(entry)

                    else:
                        sub_training_exps, sub_finished_exps = build(entry_path)
                        if sub_training_exps:
                            training_exps.append({entry: sub_training_exps})
                        if sub_finished_exps:
                            finished_exps.append({entry: sub_finished_exps})
            return training_exps, finished_exps
        return build(path)

    def update_experiment_list(self):
        """Met à jour les listes des expériences affichées."""
        tr_ids = self.training_list.get_expanded_items()
        finished_ids = self.finished_list.get_expanded_items()

        self.training_list.clear()
        self.finished_list.clear()
        self.full_experiment_list = []

        training_experiments, finished_experiments = self.build_exp_tree(self.experiments_dir)
        self.training_list.all_items = training_experiments
        self.finished_list.all_items = finished_experiments

        self.training_list.populate(training_experiments)
        self.finished_list.populate(finished_experiments)

        self.training_list.restore_expanded_items(tr_ids)
        self.finished_list.restore_expanded_items(finished_ids)

    @staticmethod
    def read_scores(file_path):
        """Lit les scores à partir d'un fichier et retourne une liste de tuples (x, y)."""
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                lines = f.readlines()
                # print(lines)
            x = []
            y = []
            for line in lines:
                values = line.strip().split(",")
                if len(values) == 1:
                    y.append(float(values[0]))
                else:
                    x.append(float(values[0]))
                    y.append(float(values[1]))
            return (x, y)

        else:
            print(f"Le fichier {file_path} n'existe pas.")
            return []

    def read_current_scores(self):
        scores_folder_path = os.path.join(self.experiments_dir, self.current_experiment_name, "scores")
        self.current_scores = {}
        if os.path.exists(scores_folder_path):
            for file_name in os.listdir(scores_folder_path):
                score = file_name.split(".")[0]
                if file_name.endswith(".txt"):
                    file_path = os.path.join(scores_folder_path, file_name)
                    x, y = self.read_scores(file_path)
                    self.current_scores[score] = (x, y)

    def read_current_flags(self):
        flags_folder_path = os.path.join(self.experiments_dir, self.current_experiment_name, "flags")
        self.current_flags = {}
        if os.path.exists(flags_folder_path):
            for file_name in os.listdir(flags_folder_path):
                flag = file_name.split(".")[0]
                if file_name.endswith(".txt"):
                    file_path = os.path.join(flags_folder_path, file_name)
                    _, x = self.read_scores(file_path)
                    self.current_flags[flag] = x

    def display_experiment(self, path):
        """Affiche le graphique de l'expérience sélectionnée."""
        self.current_experiment_name = path

        exp_path = os.path.join(self.experiments_dir, path)
        exp_info_file = os.path.join(exp_path, "exp_infos.json")

        # Charger les données des courbes
        self.read_current_scores()
        self.read_current_flags()

        # Charger et afficher l'image du modèle
        if os.path.exists(exp_info_file):
            exp_info = read_json(exp_info_file)
            model_name = exp_info.get("model_name", "")
            model_image_file = os.path.join(exp_path, f"{model_name}.png")
            self.model_image_file = model_image_file

            if os.path.exists(self.model_image_file):
                self.display_model_image()

            # if os.path.exists(model_image_file):
            #     pixmap = QPixmap(model_image_file)
            #     self.model_image_label.setPixmap(pixmap.scaled(self.model_image_label.size(),
            #                                                    aspectRatioMode=1))  # Preserve aspect ratio
            # else:
            #     self.model_image_label.clear()
            #     self.model_image_label.setText("Image non trouvée")

            # Afficher les informations du fichier JSON
            # info_text = "\n".join([f"{key} = {value}" for key, value in exp_info.items()])
            # self.exp_info_text.setText(info_text)

            sorted_keys = sorted(exp_info.keys())

            # Mettre à jour le tableau
            self.exp_info_table.setRowCount(len(sorted_keys))

            for row, key in enumerate(sorted_keys):
                value = exp_info[key]

                # Création des cellules
                key_item = QTableWidgetItem(str(key))
                value_item = QTableWidgetItem(str(value))

                # Aligner la clé à droite
                key_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                # Appliquer un fond gris clair sur une ligne sur deux
                # if row % 2 == 1:
                #     key_item.setBackground(QBrush(QColor(230, 230, 230)))  # Gris clair
                #     value_item.setBackground(QBrush(QColor(230, 230, 230)))

                # Ajouter les items dans le tableau
                self.exp_info_table.setItem(row, 0, key_item)
                self.exp_info_table.setItem(row, 1, value_item)

                # Réduire la hauteur des lignes
                self.exp_info_table.setRowHeight(row, 20)
        else:
            self.exp_info_text.setText("Aucune information disponible")

        scores_files = os.path.join(self.experiments_dir, self.current_experiment_name, "scores")
        if len(os.listdir(scores_files)) > 0:
            self.update_plot()
        else:
            self.figure.clear()
            self.canvas.draw()

    def display_model_image(self):
        if self.model_image_file is not None:
            if os.path.exists(self.model_image_file):
                image = QImage(self.model_image_file)
                if self.dark_mode_enabled:
                    image.invertPixels()
                    self.model_image_label.setStyleSheet("border: 1px solid black; background-color: black")
                else:
                    self.model_image_label.setStyleSheet("border: 1px solid black; background-color: white")
                pixmap = QPixmap.fromImage(image)
                # pixmap = QPixmap(self.model_image_file)
                self.model_image_label.setPixmap(pixmap.scaled(self.model_image_label.size(),
                                                            aspectRatioMode=Qt.KeepAspectRatio,
                                                            transformMode=Qt.SmoothTransformation))  # Preserve aspect ratio
            else:
                self.model_image_label.clear()
                self.model_image_label.setText("Image non trouvée")

    def get_curves_style(self):
        # colors
        if self.dark_mode_enabled:
            colors = read_json(self.config_file_path)["dark_mode_curves"]
        else:
            colors = read_json(self.config_file_path)["light_mode_curves"]
        ls = read_json(self.config_file_path)["curves_ls"]  # linestyle
        alpha = read_json(self.config_file_path)["curves_alpha"]  # linestyle
        return colors, ls, alpha

    def get_ma_curves_style(self):
        # colors
        if self.dark_mode_enabled:
            colors = read_json(self.config_file_path)["dark_mode_curves"]
        else:
            colors = read_json(self.config_file_path)["light_mode_curves"]
        ls = read_json(self.config_file_path)["ma_curves_ls"]  # linestyle
        alpha = read_json(self.config_file_path)["ma_curves_alpha"]  # linestyle
        return colors, ls, alpha

    def get_flags_style(self):
        # colors
        if self.dark_mode_enabled:
            colors = read_json(self.config_file_path)["dark_mode_flags"]
        else:
            colors = read_json(self.config_file_path)["light_mode_flags"]
        ls = read_json(self.config_file_path)["flags_ls"]  # linestyle
        alpha = read_json(self.config_file_path)["flags_alpha"]  # linestyle
        return colors, ls, alpha
    
    def get_plt_args(self, score_name):
        score_dir = os.path.join(self.experiments_dir, self.current_experiment_name, "scores")
        plt_args_file = os.path.join(score_dir, f"{score_name}_plt_args.json")
        if os.path.exists(plt_args_file):
            plt_args = read_json(plt_args_file)
            return plt_args
        else:
            return None

    # region - UPDATE PLOT
    def update_plot(self):
        """Met à jour le graphique avec les données actuelles et les cases cochées."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if self.dark_mode_enabled:
            bg_color = "#191919"
            text_color = "white"
            tr_color = "cyan"
            val_color = "magenta"
            best_epoch_color = text_color

        else:
            bg_color = "white"
            text_color = "black"
            tr_color = "blue"
            val_color = "orange"
            best_epoch_color = text_color

        ax.set_facecolor(bg_color)
        self.figure.set_facecolor(bg_color)
        ax.tick_params(colors=text_color)
        ax.spines['bottom'].set_color(text_color)
        ax.spines['top'].set_color(text_color)
        ax.spines['right'].set_color(text_color)
        ax.spines['left'].set_color(text_color)
        ax.xaxis.label.set_color(text_color)
        ax.yaxis.label.set_color(text_color)
        ax.title.set_color(text_color)
        # ax.grid(True, color=grid_color)

        # Loading the styles
        curves_colors, curves_ls, curves_alpha = self.get_curves_style()
        flags_colors, flags_ls, flags_alpha = self.get_flags_style()
        _, ma_curves_ls, ma_curves_alpha = self.get_ma_curves_style()

        # print('CURVE COLORS', curves_colors)

        for i, score in enumerate(self.current_scores):
            plt_args = self.get_plt_args(score)
            if plt_args is not None:
                if "color" in plt_args:
                    curves_colors[i] = plt_args["color"]
                    plt_args.pop("color")
                if "ls" in plt_args:
                    curves_ls = plt_args["ls"]
                    plt_args.pop("ls")
                if "alpha" in plt_args:
                    curves_alpha = plt_args["alpha"]
                    plt_args.pop("alpha")
            else:
                plt_args = {}
            # print("SCORE", score, "COLORS", curves_colors[i])
            x, y = self.current_scores[score]
            y_ma = compute_moving_average(y)
            if len(x) > 0:
                ax.plot(x, y, label=score, ls=curves_ls, color=curves_colors[i], alpha=curves_alpha, **plt_args)
                ax.plot(x, y_ma, label=f"{score} (MA)", ls=ma_curves_ls, color=curves_colors[i], alpha=ma_curves_alpha, **plt_args)
            else:
                ax.plot(y, label=score, ls=curves_ls, color=curves_colors[i], alpha=curves_alpha, **plt_args)
                ax.plot(y_ma, label=f"{score} (MA)", ls=ma_curves_ls, color=curves_colors[i], alpha=ma_curves_alpha, **plt_args)

        for i, flag in enumerate(self.current_flags):
            # print("FLAG", flag)
            x = self.current_flags[flag]
            print(x)
            if len(x) > 0:
                # ax.vlines(x=x, color="red", linestyle="--", label=flag)
                ax.vlines(x=x, ymin=0, ymax=1, transform=ax.get_xaxis_transform(), linestyle=flags_ls, label=flag, color=flags_colors[i], alpha=flags_alpha)

        # Afficher les courbes si les cases sont cochées
        # if self.show_train_cb.isChecked() and len(self.current_train_loss) > 0:
        #     ax.plot(self.current_train_loss, label="Train Loss", color=tr_color)

        # if self.show_train_ma_cb.isChecked() and len(self.current_train_loss) > 0:
        #     train_ma = compute_moving_average(self.current_train_loss)
        #     ax.plot(range(len(train_ma)), train_ma, label="Train Loss (MA)", color=tr_color, ls="--")

        # if self.show_val_cb.isChecked() and len(self.current_val_loss) > 0:
        #     ax.plot(self.current_val_loss, label="Validation Loss", color=val_color)

        # if self.show_val_ma_cb.isChecked() and len(self.current_val_loss) > 0:
        #     val_ma = compute_moving_average(self.current_val_loss)
        #     ax.plot(range(len(val_ma)), val_ma, label="Validation Loss (MA)", color=val_color, ls="--")

        # Ajouter une barre verticale au minimum de Validation Loss
        if len(self.current_val_loss) > 0:
            min_index = int(self.current_val_loss.argmin())  # Utilisation de numpy pour trouver l'indice du minimum
            ax.axvline(x=min_index, color=best_epoch_color, linestyle="--", label="Min Validation Loss")

        ax.set_title(self.current_experiment_name)
        ax.set_xlabel("Epochs")
        ax.set_ylabel("Loss")
        ax.legend(facecolor=bg_color, edgecolor=text_color, labelcolor=text_color)

        self.figure.tight_layout()

        self.canvas.draw()

    def refresh_graph(self):
        """Met à jour manuellement le graphique."""
        print("CURRENT FLAGS :", self.current_flags)
        print("CURRENT SCORES :", self.current_scores)
        self.list_update_timer.setInterval(self.get_interval())
        if self.current_experiment_name is not None:
            if os.path.exists(os.path.join(self.experiments_dir, self.current_experiment_name)):
                self.display_experiment(self.current_experiment_name)
            else:
                print("Aucune expérience sélectionnée. Veuillez en sélectionner une dans la liste.")
                self.figure.clear()
                self.canvas.draw()
                self.current_experiment_name = None
            # print("EXP NAME NOT NONE")
            # scores_files = os.path.join(self.experiments_dir, self.current_experiment_name, "scores")
            # if len(os.listdir(scores_files)) > 0:
            # # if os.path.exists(os.path.join(self.experiments_dir, self.current_experiment_name)):
            # # if self.current_experiment_name:  # Vérifie si une expérience est sélectionnée
            #     print("DOSSIER EXISTE")
            #     self.display_experiment(self.current_experiment_name)
            # else:
            #     print("DOSSIER EXISTE PAS")
            #     self.figure.clear()
            #     self.canvas.draw()
            #     print("FIGURE CLEARED")
            #     self.current_experiment_name = None
            #     print("Aucune expérience sélectionnée. Veuillez en sélectionner une dans la liste.")
        else:
            print("Aucune expérience sélectionnée. Veuillez en sélectionner une dans la liste.")

    def save_graph(self):
        """Enregistre le graphe actuel dans le dossier de l'expérience sélectionnée."""
        if not self.current_experiment_name:
            print("Aucune expérience sélectionnée. Veuillez en sélectionner une.")
            return

        exp_path = os.path.join(self.experiments_dir, self.current_experiment_name)
        save_path = os.path.join(exp_path, f"{self.current_experiment_name}_exp_plot.png")

        self.figure.savefig(save_path, dpi=300)  # Enregistrer en haute qualité
        print(f"Graph enregistré dans : {save_path}")

    def toggle_dark_mode(self):
        if not self.dark_mode_enabled:
            self.set_dark_mode()
            self.dark_mode_enabled = True
            self.setWindowIcon(QIcon("logo_dark.png"))
            self.dark_mode_button.setText("Light mode")
        else:
            self.set_light_mode()
            self.dark_mode_enabled = False
            self.setWindowIcon(QIcon("logo_light.png"))
            self.dark_mode_button.setText("Dark mode")

        write_json(os.path.join("xview", "config", "dark_mode.json"), {"dark_mode": self.dark_mode_enabled})
        self.update_plot()
        self.display_model_image()

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

    def finish_experiment(self):
        exp_path = os.path.join(self.experiments_dir, self.current_experiment_name)
        status_file = os.path.join(exp_path, "status.txt")
        if os.path.exists(status_file):
            write_file(status_file, "finished")
            print(f"Statut de l'expérience '{self.current_experiment_name}' mis à jour en 'finished'.")
        else:
            print(f"Le fichier de statut '{status_file}' n'existe pas.")
        # Mettre à jour la liste des expériences
        self.update_experiment_list()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyle("Fusion")

    curr_dir = os.path.abspath(os.path.dirname(__file__))
    config_path = os.path.join("xview", "config", "config.json")
    config_file_path = os.path.join(curr_dir, config_path)

    viewer = ExperimentViewer(config_file_path)
    viewer.show()

    sys.exit(app.exec_())
