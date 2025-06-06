import os
import sys
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QPushButton, QSplitter, QTextEdit, QLineEdit, QTableWidget, QTableWidgetItem)
from PyQt5.QtGui import QColor, QIcon, QPalette
from PyQt5.QtCore import QDateTime
from PyQt5.QtCore import QTimer, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from xview.utils.utils import read_file, read_json, compute_moving_average, write_file
from xview.tree_widget import MyTreeWidget
from xview.graph.curves_selector import CurvesSelector
from config import ConfigManager
from xview.version.updated_window import UpdatedNotification
from xview.version.update_project import check_for_updates
from xview.version.about_window import AboutWindow
from xview import get_config_file, set_config_data, check_config_integrity
from xview.settings.settings_window import SettingsWindow
from xview.graph.range_widget import RangeWidget
import numpy as np


# def check_for_updates():
#     """Vérifie si une mise à jour est disponible et affiche une fenêtre de mise à jour si nécessaire."""
#     last_reminder = get_config_file().get("remind_me_later_date", None)

#     # si None ou si la date est plus ancienne que 24 heures, on affiche la fenêtre de mise à jour
#     if last_reminder is None or datetime.now() - datetime.fromisoformat(last_reminder) > timedelta(hours=24):
#         if not is_up_to_date():
#             update_window = UpdateWindow()
#             update_window.exec_()


# def check_for_updates():
#     """Vérifie si une mise à jour est disponible et affiche une fenêtre de mise à jour si nécessaire."""
#     # si pas auto-update
#     if not get_config_file().get("auto_update", False):
#         last_reminder = get_config_file().get("remind_me_later_date", None)

#         # si None ou si la date est plus ancienne que 24 heures, on affiche la fenêtre de mise à jour
#         if last_reminder is None or datetime.now() - datetime.fromisoformat(last_reminder) > timedelta(hours=24):
#             if not is_up_to_date():
#                 update_window = UpdateWindow()
#                 update_window.exec_()
#     else:
#         if not is_up_to_date():
#             pull_latest_changes()
#             set_config_data("remind_me_later_date", datetime.now().isoformat())
#             set_config_data("first_since_update", True)


class ExperimentViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.experiments_dir = get_config_file()["data_folder"]
        self.current_experiment_name = None

        self.dark_mode_enabled = False

        self.model_image_file = None

        # Configurer l'interface principale
        self.setWindowTitle("XView")
        self.setWindowIcon(QIcon(os.path.join("xview", "logo_light.png")))
        self.setGeometry(100, 100, 1200, 800)

        # region - MAIN WIDGET
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Layout principal avec QSplitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(splitter)

        # region - MENU BAR
        menu_bar = self.menuBar()
        settings_menu = menu_bar.addAction("Settings")
        light_dark_menu = menu_bar.addAction("Light/Dark Mode")
        self.settings_window = None
        # exit_action = file_menu.addAction("Exit")
        settings_menu.triggered.connect(self.open_settings_window)
        light_dark_menu.triggered.connect(self.toggle_dark_mode)

        about_menu = menu_bar.addAction("About")
        about_menu.triggered.connect(lambda: AboutWindow().exec_())

        # region - LEFT WIDGET
        # Widget gauche : Contrôles et listes des expériences
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)

        # Boutons Refresh (en colonne)
        self.refresh_graph_button = QPushButton("Refresh Graph")
        self.refresh_graph_button.clicked.connect(self.refresh_graph)
        left_layout.addWidget(self.refresh_graph_button)

        self.refresh_experiments_button = QPushButton("Refresh Experiments")
        self.refresh_experiments_button.clicked.connect(self.update_experiment_list)
        left_layout.addWidget(self.refresh_experiments_button)

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

        left_layout.addWidget(save_finish_widget)

        self.config_window = None

        self.training_list = MyTreeWidget(self, display_exp=self.display_experiment, display_range=self.display_exp_range)
        self.finished_list = MyTreeWidget(self, display_exp=self.display_experiment, display_range=self.display_exp_range)

        left_layout.addWidget(QLabel("Experiments in progress"))
        left_layout.addWidget(self.training_list)
        left_layout.addWidget(QLabel("Finished experiments"))

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search for an experiment...")
        # self.search_bar.textChanged.connect(self.filter_experiments)
        self.search_bar.textChanged.connect(self.finished_list.filter_items)
        left_layout.addWidget(self.search_bar)  # Ajout sous le titre "Expériences terminées"

        left_layout.addWidget(self.finished_list)  # Liste des expériences terminées sous la barre de recherche

        # region - PLOT WIDGET
        # Widget central : Graphique Matplotlib
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        splitter.addWidget(self.canvas)

        # region - RIGHT WIDGET
        # Widget droit : Affichage du schéma du modèle et des informations
        right_widget = QSplitter(Qt.Vertical)
        splitter.addWidget(right_widget)

        # region - plot range
        self.range_widget = RangeWidget()
        self.range_widget.setFixedHeight(165)
        self.range_widget.setMinimumWidth(240)
        right_widget.addWidget(self.range_widget)
        # ------------------------ x axis
        self.range_widget.x_min.editingFinished.connect(
            lambda: self.set_exp_config_data("x_min", self.range_widget.x_min.text()))
        self.range_widget.x_max.editingFinished.connect(
            lambda: self.set_exp_config_data("x_max", self.range_widget.x_max.text()))
        # ------------------------ y axis
        self.range_widget.y_min.editingFinished.connect(
            lambda: self.set_exp_config_data("y_min", self.range_widget.y_min.text()))
        self.range_widget.y_max.editingFinished.connect(
            lambda: self.set_exp_config_data("y_max", self.range_widget.y_max.text()))

        self.curve_selector_widget = CurvesSelector(self)
        right_widget.addWidget(self.curve_selector_widget)

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

        # region - QTIMER
        # Timers pour mise à jour
        self.list_update_timer = QTimer(self)
        self.list_update_timer.timeout.connect(self.update_experiment_list)
        # self.list_update_timer.timeout.connect(self.update_plot)  # Mise à jour du graphique en même temps que les listes
        self.list_update_timer.timeout.connect(self.refresh_graph)  # Mise à jour du graphique en même temps que les listes
        self.list_update_timer.start(self.get_interval())

        self.update_check_timer = QTimer(self)
        self.update_check_timer.timeout.connect(check_for_updates)
        # vérification toutes les 60 minutes
        self.update_check_timer.start(60 * 60 * 1000)  # 60 minutes en millisecondes
        # self.update_check_timer.start(5 * 1000)  # 60 minutes en millisecondes

        # Variables pour le stockage temporaire
        self.current_scores = {}
        self.current_flags = {}
        self.current_train_loss = []
        self.current_val_loss = []

        self.set_dark_mode(get_config_file()["dark_mode"])

        # Mise à jour initiale
        self.update_experiment_list()
        self.update_plot()

        first_since_update = get_config_file().get("first_since_update", None)

        if first_since_update is None:
            set_config_data("first_since_update", True)
            upd_notif = UpdatedNotification()
            upd_notif.exec_()
            set_config_data("first_since_update", False)
        elif first_since_update:
            upd_notif = UpdatedNotification()
            upd_notif.exec_()
            set_config_data("first_since_update", False)

    def read_dark_mode_state(self):
        """Lit l'état du mode sombre à partir du fichier JSON."""
        return get_config_file()["dark_mode"]

    def get_interval(self):
        interval = get_config_file()["update_interval"]
        return int(interval * 1000)

    def open_config_panel(self):
        if self.config_window is None or not self.config_window.isVisible():
            # self.config_window = ConfigManager(self.config_file_path)
            self.config_window = ConfigManager()
            self.config_window.show()
        else:
            self.config_window.activateWindow()
            self.config_window.raise_()

    def open_settings_window(self):
        if self.settings_window is None or not self.settings_window.isVisible():
            # self.config_window = ConfigManager(self.config_file_path)
            self.settings_window = SettingsWindow(main_gui=self)
            self.settings_window.show()
        else:
            self.settings_window.activateWindow()
            self.settings_window.raise_()

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
        self.experiments_dir = get_config_file()["data_folder"]

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
                if file_name.endswith(".txt") and not score.endswith("_label_value"):
                    file_path = os.path.join(scores_folder_path, file_name)
                    x, y = self.read_scores(file_path)
                    self.current_scores[score] = (x, y)

    def read_current_flags(self):
        flags_folder_path = os.path.join(self.experiments_dir, self.current_experiment_name, "flags")
        self.current_flags = {}
        if os.path.exists(flags_folder_path):
            for file_name in os.listdir(flags_folder_path):
                flag = file_name.split(".")[0]
                if file_name.endswith(".txt") and not flag.endswith("_label_value"):
                    file_path = os.path.join(flags_folder_path, file_name)
                    _, x = self.read_scores(file_path)
                    self.current_flags[flag] = x

    def display_exp_range(self):
        x_min = self.get_exp_config_data("x_min")
        if x_min is None:
            x_min = ""
        else:
            x_min = str(x_min)

        x_max = self.get_exp_config_data("x_max")
        if x_max is None:
            x_max = ""
        else:
            x_max = str(x_max)

        y_min = self.get_exp_config_data("y_min")
        if y_min is None:
            y_min = ""
        else:
            y_min = str(y_min)

        y_max = self.get_exp_config_data("y_max")
        if y_max is None:
            y_max = ""
        else:
            y_max = str(y_max)

        self.range_widget.x_min.setText(x_min)
        self.range_widget.x_max.setText(x_max)
        self.range_widget.y_min.setText(y_min)
        self.range_widget.y_max.setText(y_max)

        normalize = self.get_exp_config_data("normalize")
        if normalize is None:
            normalize = False
        self.range_widget.normalize_checkbox.setChecked(normalize)
        self.range_widget.normalize_checkbox.stateChanged.connect(self.normalized_state_changed)

    def normalized_state_changed(self):
        """Gère le changement d'état de la case à cocher de normalisation."""
        normalize = self.range_widget.normalize_checkbox.isChecked()
        self.set_exp_config_data("normalize", normalize)

    # region - display_experiment
    def display_experiment(self, path):
        """Affiche le graphique de l'expérience sélectionnée."""
        self.current_experiment_name = path

        exp_path = os.path.join(self.experiments_dir, path)
        exp_info_file = os.path.join(exp_path, "exp_infos.json")

        # Charger les données des courbes
        self.read_current_scores()
        self.read_current_flags()

        if exp_path != self.curve_selector_widget.current_path:
            self.curve_selector_widget.reset_window(exp_path)
            self.curve_selector_widget.init_boxes(
                self.current_scores.keys(), self.current_flags.keys()
            )
        else:
            self.curve_selector_widget.update_boxes(
                self.current_scores.keys(), self.current_flags.keys()
            )

        if os.path.exists(exp_info_file):
            exp_info = read_json(exp_info_file)
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

    # def display_model_image(self):
    #     if self.model_image_file is not None:
    #         if os.path.exists(self.model_image_file):
    #             image = QImage(self.model_image_file)
    #             if self.dark_mode_enabled:
    #                 image.invertPixels()
    #                 self.model_image_label.setStyleSheet("border: 1px solid black; background-color: black")
    #             else:
    #                 self.model_image_label.setStyleSheet("border: 1px solid black; background-color: white")
    #             pixmap = QPixmap.fromImage(image)
    #             self.model_image_label.setPixmap(pixmap.scaled(self.model_image_label.size(),
    #                                                            aspectRatioMode=Qt.KeepAspectRatio,
    #                                                            transformMode=Qt.SmoothTransformation))  # Preserve aspect ratio
    #         else:
    #             self.model_image_label.clear()
    #             self.model_image_label.setText("Image non trouvée")

    def get_curves_style(self):
        # colors
        if self.dark_mode_enabled:
            colors = get_config_file()["dark_mode_curves"]
        else:
            colors = get_config_file()["light_mode_curves"]
        ls = get_config_file()["curves_ls"]  # linestyle
        alpha = get_config_file()["curves_alpha"]  # linestyle
        return colors, ls, alpha

    def get_ma_curves_style(self):
        # colors
        if self.dark_mode_enabled:
            colors = get_config_file()["dark_mode_curves"]
        else:
            colors = get_config_file()["light_mode_curves"]
        ls = get_config_file()["ma_curves_ls"]  # linestyle
        alpha = get_config_file()["ma_curves_alpha"]  # linestyle
        return colors, ls, alpha

    def get_flags_style(self):
        # colors
        if self.dark_mode_enabled:
            colors = get_config_file()["dark_mode_flags"]
        else:
            colors = get_config_file()["light_mode_flags"]
        ls = get_config_file()["flags_ls"]  # linestyle
        alpha = get_config_file()["flags_alpha"]  # linestyle
        return colors, ls, alpha

    def get_plt_args(self, score_name, type):
        score_dir = os.path.join(self.experiments_dir, self.current_experiment_name, type)
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

        else:
            bg_color = "white"
            text_color = "black"

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

        # Loading the styles
        curves_colors, curves_ls, curves_alpha = self.get_curves_style()
        flags_colors, flags_ls, flags_alpha = self.get_flags_style()
        _, ma_curves_ls, ma_curves_alpha = self.get_ma_curves_style()

        # print('CURVE COLORS', curves_colors)
        x_min, x_max = None, None
        y_min, y_max = None, None

        for i, score in enumerate(self.current_scores):
            plt_args = self.get_plt_args(score, type="scores")
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

            x, y = self.current_scores[score]
            y_ma = compute_moving_average(y)

            if os.path.exists(
                os.path.join(self.experiments_dir, self.current_experiment_name, "scores", f"{score}_label_value.txt")
            ):
                label_file = os.path.join(self.experiments_dir, self.current_experiment_name, "scores", f"{score}_label_value.txt")
                label_value = read_file(label_file, return_str=True)
            else:
                label_value = ""

            if self.get_exp_config_data("normalize"):
                #  normalisation 0 1
                y = np.array(y)
                y_ma = np.array(y_ma)
                if len(x) > 0:
                    y = (y - np.min(y)) / (np.max(y) - np.min(y))
                    y_ma = (y_ma - np.min(y_ma)) / (np.max(y_ma) - np.min(y_ma))
                else:
                    y = (y - np.min(y)) / (np.max(y) - np.min(y))
                    y_ma = (y_ma - np.min(y_ma)) / (np.max(y_ma) - np.min(y_ma))

            if len(x) > 0:
                if self.curve_selector_widget.boxes[score][0].isChecked():
                    ax.plot(x, y, label=f"{label_value} {score}", ls=curves_ls, color=curves_colors[i], alpha=curves_alpha, **plt_args)
                if self.curve_selector_widget.boxes[f"{score} (MA)"][0].isChecked():
                    ax.plot(x, y_ma, label=f"{score} (MA)", ls=ma_curves_ls, color=curves_colors[i], alpha=ma_curves_alpha, **plt_args)
            else:
                if self.curve_selector_widget.boxes[score][0].isChecked():
                    ax.plot(y, label=f"{label_value} {score}", ls=curves_ls, color=curves_colors[i], alpha=curves_alpha, **plt_args)
                if self.curve_selector_widget.boxes[f"{score} (MA)"][0].isChecked():
                    ax.plot(y_ma, label=f"{score} (MA)", ls=ma_curves_ls, color=curves_colors[i], alpha=ma_curves_alpha, **plt_args)

        #  ------------------------------------------- PLOT RANGE
        # ------------------------------- X AXIS RANGE
        if self.current_experiment_name is not None:
            x_min = self.get_exp_config_data("x_min")
            if x_min == "" or x_min is None:
                x_min = None
            else:
                x_min = float(x_min)
            x_max = self.get_exp_config_data("x_max")
            if x_max == "" or x_max is None:
                x_max = None
            else:
                x_max = float(x_max)

            # ------------------------------- Y AXIS RANGE
            y_min = self.get_exp_config_data("y_min")
            if y_min == "" or y_min is None:
                y_min = None
            else:
                y_min = float(y_min)
            y_max = self.get_exp_config_data("y_max")
            if y_max == "" or y_max is None:
                y_max = None
            else:
                y_max = float(y_max)

        for i, flag in enumerate(self.current_flags):
            plt_args = self.get_plt_args(flag, type="flags")
            if plt_args is not None:
                if "color" in plt_args:
                    flags_colors[i] = plt_args["color"]
                    plt_args.pop("color")
                if "ls" in plt_args:
                    flags_ls = plt_args["ls"]
                    plt_args.pop("ls")
                if "alpha" in plt_args:
                    flags_alpha = plt_args["alpha"]
                    plt_args.pop("alpha")
            else:
                plt_args = {}

            if os.path.exists(
                os.path.join(self.experiments_dir, self.current_experiment_name, "flags", f"{flag}_label_value.txt")
            ):
                label_file = os.path.join(self.experiments_dir, self.current_experiment_name, "flags", f"{flag}_label_value.txt")
                label_value = read_file(label_file, return_str=True)
            else:
                label_value = ""

            x = self.current_flags[flag]
            if self.curve_selector_widget.boxes[flag][0].isChecked():
                label = f"{label_value} {flag}"
                label_written = False
                for xo in x:
                    ax.axvline(x=xo, linestyle=flags_ls, label=label if not label_written else None, color=flags_colors[i], alpha=flags_alpha, **plt_args)
                    label_written = True

        ax.set_xlim(x_min if x_min is not None else ax.get_xlim()[0],
                    x_max if x_max is not None else ax.get_xlim()[1])
        ax.set_ylim(y_min if y_max is not None else ax.get_ylim()[0],
                    y_max if y_max is not None else ax.get_ylim()[1])

        ax.set_title(self.current_experiment_name)
        ax.set_xlabel("Epochs")
        ax.set_ylabel("Loss")
        if self.range_widget.legend_checkbox.isChecked():
            ax.legend(loc='upper right', facecolor=bg_color, edgecolor=text_color, labelcolor=text_color)
            ax.legend(facecolor=bg_color, edgecolor=text_color, labelcolor=text_color)

        self.figure.tight_layout()

        self.canvas.draw()

    def refresh_graph(self):
        """Met à jour manuellement le graphique."""
        self.list_update_timer.setInterval(self.get_interval())
        if self.current_experiment_name is not None:
            if os.path.exists(os.path.join(self.experiments_dir, self.current_experiment_name)):
                self.display_experiment(self.current_experiment_name)
            else:
                # print("Aucune expérience sélectionnée. Veuillez en sélectionner une dans la liste.")
                self.figure.clear()
                self.canvas.draw()
                self.current_experiment_name = None
        # else:
        #     print("Aucune expérience sélectionnée. Veuillez en sélectionner une dans la liste.")

    def save_graph(self):
        """Enregistre le graphe actuel dans le dossier de l'expérience sélectionnée."""
        if not self.current_experiment_name:
            # print("Aucune expérience sélectionnée. Veuillez en sélectionner une.")
            return

        exp_figure_path = os.path.join(self.experiments_dir, self.current_experiment_name, 'figures')

        if not os.path.exists(exp_figure_path):
            os.makedirs(exp_figure_path)

        # format yyyy-mm-dd_HH-MM-SS
        figure_date = QDateTime.currentDateTime().toString("yyyy-MM-dd_HH-mm-ss")

        save_path = os.path.join(exp_figure_path, f"{figure_date}.png")

        self.figure.savefig(save_path, dpi=300)  # Enregistrer en haute qualité
        print(f"Graph enregistré dans : {save_path}")

    def set_dark_mode(self, sett):
        if sett:
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
            self.setWindowIcon(QIcon(os.path.join("xview", "logo_dark.png")))
            # self.dark_mode_button.setText("Light mode")
            self.dark_mode_enabled = True
        else:
            self.setPalette(QApplication.style().standardPalette())
            self.setWindowIcon(QIcon(os.path.join("xview", "logo_light.png")))
            # self.dark_mode_button.setText("Dark mode")
            self.dark_mode_enabled = False

        self.update_plot()

        set_config_data("dark_mode", sett)

    def toggle_dark_mode(self):
        self.set_dark_mode(not get_config_file()["dark_mode"])
        # self.update_plot()
        # self.display_model_image()

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

    def get_exp_config_file(self):
        if not os.path.exists(os.path.join(self.experiments_dir, self.current_experiment_name, "config.json")):
            self.set_exp_config_file({})
        config = json.load(open(os.path.join(self.experiments_dir, self.current_experiment_name, "config.json")))
        return config

    def get_exp_config_data(self, key):
        return self.get_exp_config_file().get(key, None)

    def set_exp_config_file(self, config):
        with open(os.path.join(self.experiments_dir, self.current_experiment_name, "config.json"), "w") as f:
            json.dump(config, f, indent=4)

    def set_exp_config_data(self, key, value):
        config = self.get_exp_config_file()
        config[key] = value
        self.set_exp_config_file(config)

    def add_curve_color(self, color):
        """Ajoute une couleur à la liste des couleurs de courbes."""
        dark_colors = get_config_file()["dark_mode_curves"]
        light_colors = get_config_file()["light_mode_curves"]

        if self.dark_mode_enabled:
            dark_colors.append(color)
            # set_config_data("dark_mode_curves", dark_colors)
            # on ajoute un trait noir (en hexa) en light mode
            light_colors.append("#000000")
            # set_config_data("light_mode_curves", light_colors)
        else:
            light_colors.append(color)
            # set_config_data("light_mode_curves", light_colors)
            # on ajoute un trait blanc (en hexa) en dark mode
            dark_colors.append("#FFFFFF")
            # set_config_data("dark_mode_curves", dark_colors)

        set_config_data("dark_mode_curves", dark_colors)
        set_config_data("light_mode_curves", light_colors)

    def remove_curve_color(self, index):
        dark_colors = get_config_file()["dark_mode_curves"]
        light_colors = get_config_file()["light_mode_curves"]

        if index < len(dark_colors):
            dark_colors.pop(index)
        if index < len(light_colors):
            light_colors.pop(index)

        set_config_data("dark_mode_curves", dark_colors)
        set_config_data("light_mode_curves", light_colors)

        self.settings_window.settings_widgets["Display"].curve_color_widget.colors = dark_colors if self.dark_mode_enabled else light_colors

    def add_flag_color(self, color):
        """Ajoute une couleur à la liste des couleurs de courbes."""
        dark_colors = get_config_file()["dark_mode_flags"]
        light_colors = get_config_file()["light_mode_flags"]

        if self.dark_mode_enabled:
            dark_colors.append(color)
            # set_config_data("dark_mode_curves", dark_colors)
            # on ajoute un trait noir (en hexa) en light mode
            light_colors.append("#000000")
            # set_config_data("light_mode_curves", light_colors)
        else:
            light_colors.append(color)
            # set_config_data("light_mode_curves", light_colors)
            # on ajoute un trait blanc (en hexa) en dark mode
            dark_colors.append("#FFFFFF")
            # set_config_data("dark_mode_curves", dark_colors)

        set_config_data("dark_mode_flags", dark_colors)
        set_config_data("light_mode_flags", light_colors)

    def remove_flag_color(self, index):
        dark_colors = get_config_file()["dark_mode_flags"]
        light_colors = get_config_file()["light_mode_flags"]

        if index < len(dark_colors):
            dark_colors.pop(index)
        if index < len(light_colors):
            light_colors.pop(index)

        set_config_data("dark_mode_flags", dark_colors)
        set_config_data("light_mode_flags", light_colors)

        self.settings_window.settings_widgets["Display"].flag_color_widget.colors = dark_colors if self.dark_mode_enabled else light_colors


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    check_config_integrity()

    check_for_updates()

    # if not is_up_to_date():
    #     if not get_config_file().get("auto_update", False):
    #         check_for_updates()
    #     else:
    #         pull_latest_changes()

    curr_dir = os.path.abspath(os.path.dirname(__file__))

    viewer = ExperimentViewer()
    viewer.show()

    sys.exit(app.exec_())
