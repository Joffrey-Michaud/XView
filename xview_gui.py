"""Main XView GUI to browse experiments, plot scores, and manage settings."""

import sys
from pathlib import Path

# Configure logging early and robustly (works on Ubuntu and WSL2)

if 'nolog' not in sys.argv:
    log_file = Path.home() / ".xview" / "xview.log"
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        # Line-buffered append to preserve history across runs
        sys.stdout = open(log_file, "a", buffering=1, encoding="utf-8", errors="backslashreplace")
        sys.stderr = sys.stdout  # Capture errors too
    except Exception:
        # Fall back to console if logging cannot be initialized
        pass

# Print a launch banner with date and version at the top of each run
try:
    from datetime import datetime
    version = "unknown"
    try:
        # Try reading from user config first
        from xview import get_config_file, default_config
        try:
            cfg = get_config_file()
        except Exception:
            cfg = None
        version = (cfg and cfg.get("version")) or default_config.get("version") or "unknown"
    except Exception:
        pass
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("#---------------------------------------------------------#")
    print(f"[XView] Start {ts} | version={version}")
except Exception:
    # Ignore banner failures
    pass

import os
import time
import datetime
import shutil
import random
import json
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QPushButton, QSplitter, QTextEdit, QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox)
from PyQt5.QtGui import QColor, QIcon, QPalette, QClipboard
from PyQt5.QtCore import QDateTime
from PyQt5.QtCore import QTimer, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from xview.utils.utils import read_file, read_json, compute_moving_average, write_file
from xview.utils.plot_utils import plot_monitoring_lines
from xview.tree_widget import MyTreeWidget
from xview.graph.curves_selector import CurvesSelector
from config import ConfigManager
from xview.version.updated_window import UpdatedNotification
from xview.version.update_project import check_for_updates
from xview.version.about_window import AboutWindow
from xview import get_config_file, set_config_data, check_config_integrity, get_config_data, CONFIG_FILE_DIR
from xview.settings.settings_window import SettingsWindow
from xview.graph.range_widget import RangeWidget
from xview.settings.palette import Palette
import numpy as np
import subprocess
import tempfile
import platform


class ExperimentViewer(QMainWindow):
    """Primary window showing experiment lists, plots, and info panels."""

    def __init__(self):
        super().__init__()

        self.experiments_dir = get_config_file()["data_folder"]
        self.current_experiment_name = None

        self.dark_mode_enabled = False

        self.model_image_file = None

        self.palette = Palette(get_config_data("palette_name"))

        # Configurer l'interface principale
        self.setWindowTitle("XView")
        #  trouver le dossier du script
        LOGO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "xview", "logo_light.png")
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), "xview", "logo_light.png")))
        self.setGeometry(100, 100, 1200, 800)

        self.widget_sizes = get_config_data("widget_sizes")

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

        self.screenshot_graph_button = QPushButton("Screenshot graph")
        self.screenshot_graph_button.clicked.connect(self.screenshot_graph)
        left_layout.addWidget(self.screenshot_graph_button)

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

        self.training_list = MyTreeWidget(self, display_exp=self.display_experiment, display_range=self.display_exp_range, remove_folders_callback=self.remove_folders, move_exp_callback=self.move_exp, copy_exp_callback=self.copy_exp)
        self.finished_list = MyTreeWidget(self, display_exp=self.display_experiment, display_range=self.display_exp_range, remove_folders_callback=self.remove_folders, move_exp_callback=self.move_exp, copy_exp_callback=self.copy_exp)

        left_layout.addWidget(QLabel("Experiments in progress"))
        left_layout.addWidget(self.training_list)
        left_layout.addWidget(QLabel("Finished experiments"))

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search for an experiment...")
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

        self.curve_selector_widget = CurvesSelector(self, update_plot_callback=self.update_plot)
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

        # region - QTIMERs
        # Timers pour mise à jour
        self.list_update_timer = QTimer(self)
        self.list_update_timer.timeout.connect(self.update_experiment_list)
        self.list_update_timer.timeout.connect(self.refresh_graph)  # Mise à jour du graphique en même temps que les listes
        self.list_update_timer.start(0)

        self.update_check_timer = QTimer(self)
        self.update_check_timer.timeout.connect(check_for_updates)
        self.update_check_timer.start(0)

        self.trash_cleanup_timer = QTimer(self)
        self.trash_cleanup_timer.timeout.connect(self.cleanup_trash)
        self.trash_cleanup_timer.start(0)

        self.remote_fetch_timer = QTimer(self)
        self.remote_fetch_timer.timeout.connect(self.fetch_remote_data)
        self.remote_fetch_timer.start(0)

        # Variables pour le stockage temporaire
        self.current_scores = {}
        self.current_flags = {}
        self.current_train_loss = []
        self.current_val_loss = []

        self.set_dark_mode(get_config_file()["dark_mode"])

        # set widget sizes
        if self.widget_sizes:
            left_width, plot_width, right_width = self.widget_sizes
            splitter.setSizes([left_width, plot_width, right_width])
        else:
            # Set default sizes if not available
            splitter.setSizes([200, 400, 200])

        # Mise à jour initiale
        self.update_experiment_list()
        self.update_plot()
        self.cleanup_trash()

        self.setup_timers()

    def setup_timers(self):
        """Configure periodic timers for list updates, updates check, and trash cleanup."""
        self.list_update_timer.setInterval(max(2000, self.get_interval()))
        self.update_check_timer.setInterval(60 * 60 * 1000)

        # setting up trash clean up timer every 60 minutes
        self.trash_cleanup_timer.setInterval(60 * 60 * 1000)

        self.remote_fetch_timer.setInterval(1000 * int(get_config_data("remote_fetch_interval")))

    # -----------------------------------------------------------------------------------------
    # region - TRASH
    def get_trash_dir(self):
        """Return the configured Trash directory (default ~/.xview/Trash)."""
        trash_dir = get_config_data("trash_dir")
        if trash_dir is None:
            trash_dir = os.path.join(CONFIG_FILE_DIR, "Trash")
            set_config_data("trash_dir", trash_dir)
        return trash_dir

    def _entry_ctime(self, p):
        """Safe creation time for a path, returning 0 on failure."""
        try:
            return p.stat().st_ctime
        except Exception:
            return 0.0

    def _get_dir_size(self, p):
        """Recursively compute directory size in bytes; ignore unreadable files."""
        total = 0
        try:
            if p.is_file():
                return p.stat().st_size
            for root, dirs, files in os.walk(p):
                for f in files:
                    try:
                        fp = Path(root) / f
                        total += fp.stat().st_size
                    except Exception:
                        pass
        except Exception:
            pass
        return total

    def _remove_path(self, p):
        """Remove a directory tree; log errors but continue."""
        try:
            if p.is_dir():
                shutil.rmtree(p)
        except Exception as e:
            print(f"Error removing {p}: {e}")

    def cleanup_trash(self):
        """Clean the Trash folder based on max days and max size limits."""
        print("CLEANING TRASH DIR")
        trash_dir = self.get_trash_dir()
        if not os.path.exists(trash_dir):
            return

        trash_dir = Path(trash_dir)

        # 1. Clean the folders if they exceed the max days
        max_days = get_config_data("trash_max_days")
        now = time.time()
        if max_days and max_days > 0:
            cutoff = now - (max_days * 86400)  # 86400 seconds in a day
            for item in trash_dir.iterdir():
                try:
                    if self._entry_ctime(item) < cutoff:
                        self._remove_path(item)
                except Exception as e:
                    print(f"Error cleaning up {item}: {e}")

        # 2. Clean the folders if they exceed the max size
        max_size_gb = get_config_data("trash_max_size")  # taille en Gb
        if max_size_gb and max_size_gb > 0:
            limit_bytes = max_size_gb * 1024 * 1024 * 1024
            total = sum(self._get_dir_size(item) for item in trash_dir.iterdir())
            if total > limit_bytes:
                # Sort items by modification time (oldest first)
                items = sorted(trash_dir.iterdir(), key=self._entry_mtime)
                for item in items:
                    if total <= limit_bytes:
                        break
                    size = self._get_dir_size(item)
                    self._remove_path(item)
                    total -= size

    def read_dark_mode_state(self):
        """Return dark mode boolean from the config file."""
        return get_config_file()["dark_mode"]

    def get_interval(self):
        """Get list/plot refresh interval in seconds as an int milliseconds value."""
        interval = get_config_file()["update_interval"]
        return int(interval * 1000)

    def open_config_panel(self):
        """Open the legacy config panel window (if not already visible)."""
        if self.config_window is None or not self.config_window.isVisible():
            # self.config_window = ConfigManager(self.config_file_path)
            self.config_window = ConfigManager()
            self.config_window.show()
        else:
            self.config_window.activateWindow()
            self.config_window.raise_()

    def open_settings_window(self):
        """Open the settings window for palettes and preferences."""
        if self.settings_window is None or not self.settings_window.isVisible():
            # self.config_window = ConfigManager(self.config_file_path)
            self.settings_window = SettingsWindow(main_gui=self, palette=self.palette)
            self.settings_window.show()
        else:
            self.settings_window.activateWindow()
            self.settings_window.raise_()

    def toggle_model_image(self):
        """Show or hide the model image and info based on a checkbox state."""
        if self.show_network_cb.isChecked():
            self.model_image_label.show()
            self.exp_info_text.show()
        else:
            self.model_image_label.hide()
            self.exp_info_text.hide()

    def filter_experiments(self):
        """Filter finished experiments list using the search bar text."""
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
        """Refresh training and finished experiments trees and preserve expansion."""
        self.experiments_dir = get_config_file()["data_folder"]

        tr_ids = self.training_list.get_expanded_items()
        finished_ids = self.finished_list.get_expanded_items()

        self.training_list.clear()
        self.finished_list.clear()
        self.full_experiment_list = []

        training_experiments, finished_experiments = self.build_exp_tree(self.experiments_dir)
        self.training_list.all_items = training_experiments
        self.finished_list.all_items = finished_experiments

        # Populate training list normally
        self.training_list.populate(training_experiments)

        # Keep current filter on finished list across updates
        current_filter = self.search_bar.text().strip()
        if current_filter:
            # filter_items repopulates based on all_items
            self.finished_list.filter_items(current_filter)
        else:
            self.finished_list.populate(finished_experiments)

        self.training_list.restore_expanded_items(tr_ids)
        self.finished_list.restore_expanded_items(finished_ids)

    @staticmethod
    def read_scores(file_path):
        """Read score file and return (x, y) arrays; supports one- or two-column format."""
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
        """Populate the range widget with the current experiment's stored bounds."""
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
        """Handle normalize checkbox toggling and persist the new value."""
        normalize = self.range_widget.normalize_checkbox.isChecked()
        self.set_exp_config_data("normalize", normalize)

    # region - display_experiment
    def display_experiment(self, path):
        """Load scores/flags for the selected experiment and redraw the plot."""
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

    def get_curves_style(self):
        colors = self.palette.light_mode_curves if not self.dark_mode_enabled else self.palette.dark_mode_curves
        return colors, self.palette.curves_ls, self.palette.curves_alpha

    def get_ma_curves_style(self):
        colors = self.palette.light_mode_curves if not self.dark_mode_enabled else self.palette.dark_mode_curves
        return colors, self.palette.ma_curves_ls, self.palette.ma_curves_alpha

    def get_flags_style(self):
        colors = self.palette.light_mode_flags if not self.dark_mode_enabled else self.palette.dark_mode_flags
        return colors, self.palette.flags_ls, self.palette.flags_alpha

    def get_plt_args(self, score_name, type):
        score_dir = os.path.join(self.experiments_dir, self.current_experiment_name, type)
        plt_args_file = os.path.join(score_dir, f"{score_name}_plt_args.json")
        if os.path.exists(plt_args_file):
            plt_args = read_json(plt_args_file)
            return plt_args
        else:
            return None

    def save_widget_sizes(self):
        """Save current splitter sizes (left/plot/right) into config for persistence."""
        # Get the sizes from the main splitter
        sizes = self.centralWidget().layout().itemAt(0).widget().sizes()

        if len(sizes) == 3:
            left_width = sizes[0]
            plot_width = sizes[1]
            right_width = sizes[2]

            set_config_data("widget_sizes", (left_width, plot_width, right_width))

    def get_scores_monitoring(self):
        return self.get_exp_config_data("scores_monitoring")

    # region - UPDATE PLOT
    def update_plot(self):
        """Update the Matplotlib plot based on selected scores, flags, and options."""
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

        try:
            scores_monitoring = self.get_scores_monitoring()
        except:
            scores_monitoring = {}

        # ensure compatibility with older exmperiment
        if scores_monitoring is None:
            scores_monitoring = {}
            for score in self.current_scores:
                scores_monitoring[score] = "max"

        random.seed(159)

        #  ----------------------------------------------------------- GET RANDOM COLORS
        if len(curves_colors) < len(self.current_scores):
            #  if not enough colors, we add more

            for i in range(len(curves_colors), len(self.current_scores)):
                random_col = "#{:06x}".format(random.randint(0, 0xFFFFFF)).upper()
                while random_col in curves_colors:
                    random_col = "#{:06x}".format(random.randint(0, 0xFFFFFF)).upper()
                curves_colors.append(random_col)

        if len(flags_colors) < len(self.current_flags):
            #  if not enough colors, we add more
            for i in range(len(flags_colors), len(self.current_flags)):
                random_col = "#{:06x}".format(random.randint(0, 0xFFFFFF)).upper()
                while random_col in curves_colors:
                    random_col = "#{:06x}".format(random.randint(0, 0xFFFFFF)).upper()
                flags_colors.append(random_col)

        x_min, x_max = None, None
        y_min, y_max = None, None

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
            y_ma = compute_moving_average(y, window_size=get_config_data("ma_window_size"))

            if os.path.exists(
                os.path.join(self.experiments_dir, self.current_experiment_name, "scores", f"{score}_label_value.txt")
            ):
                label_file = os.path.join(self.experiments_dir, self.current_experiment_name, "scores", f"{score}_label_value.txt")
                label_value = read_file(label_file, return_str=True)
            else:
                label_value = ""

            #  ----------------------------------------------------------- NORMALIZE IF NEEDED
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

            #  ----------------------------------------------------------- PLOT CURVES
            monitoring_modes = scores_monitoring[score]
            if len(x) > 0:
                if self.curve_selector_widget.boxes[score][0].isChecked():  #  score
                    ax.plot(x, y, label=f"{label_value} {score}", ls=curves_ls, color=curves_colors[i], alpha=curves_alpha, **plt_args)
                    if self.range_widget.optimum_checkbox.isChecked():
                        plot_monitoring_lines(ax, x, y, color=curves_colors[i], monitoring_flags=monitoring_modes, ls="-.", alpha=curves_alpha, x_max_range=x_max)
                if self.curve_selector_widget.boxes[f"{score} (MA)"][0].isChecked():  # score MA
                    ax.plot(x, y_ma, label=f"{score} (MA)", ls=ma_curves_ls, color=curves_colors[i], alpha=ma_curves_alpha, **plt_args)
                    if self.range_widget.optimum_checkbox.isChecked():
                        plot_monitoring_lines(ax, x, y_ma, color=curves_colors[i], monitoring_flags=monitoring_modes, ls="-.", alpha=ma_curves_alpha, x_max_range=x_max)
            else:
                if self.curve_selector_widget.boxes[score][0].isChecked():
                    ax.plot(y, label=f"{label_value} {score}", ls=curves_ls, color=curves_colors[i], alpha=curves_alpha, **plt_args)
                    if self.range_widget.optimum_checkbox.isChecked():
                        xx = np.arange(len(y))
                        plot_monitoring_lines(ax, xx, y, color=curves_colors[i], monitoring_flags=monitoring_modes, ls="-.", alpha=curves_alpha, x_max_range=x_max)
                if self.curve_selector_widget.boxes[f"{score} (MA)"][0].isChecked():
                    ax.plot(y_ma, label=f"{score} (MA)", ls=ma_curves_ls, color=curves_colors[i], alpha=ma_curves_alpha, **plt_args)
                    if self.range_widget.optimum_checkbox.isChecked():
                        xx = np.arange(len(y))
                        plot_monitoring_lines(ax, xx, y_ma, color=curves_colors[i], monitoring_flags=monitoring_modes, ls="-.", alpha=ma_curves_alpha, x_max_range=x_max)

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

            #  ----------------------------------------------------------- PLOT FLAGS
            x = self.current_flags[flag]
            if self.curve_selector_widget.boxes[flag][0].isChecked():
                label = f"{label_value} {flag}"
                label_written = False
                for xo in x:
                    ax.axvline(x=xo, linestyle=flags_ls, label=label if not label_written else None, color=flags_colors[i], alpha=flags_alpha, **plt_args)
                    label_written = True

        ax.set_xlim(x_min if x_min is not None else ax.get_xlim()[0],
                    x_max if x_max is not None else ax.get_xlim()[1])
        ax.set_ylim(y_min if y_min is not None else ax.get_ylim()[0],
                    y_max if y_max is not None else ax.get_ylim()[1])

        ax.set_title(self.current_experiment_name)
        ax.set_xlabel("Epochs")
        ax.set_ylabel("Loss")
        if self.range_widget.legend_checkbox.isChecked():
            ax.legend(loc='upper right', facecolor=bg_color, edgecolor=text_color, labelcolor=text_color)
            ax.legend(facecolor=bg_color, edgecolor=text_color, labelcolor=text_color)

        self.figure.tight_layout()

        self.canvas.draw()

        self.save_widget_sizes()

    def refresh_graph(self):
        """Manually refresh the plot and selection if current experiment changed."""
        self.setup_timers()
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
        """Save the current plot as a PNG under the experiment's figures folder."""
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

    # -----------------------------------------------------------------------------------------
    # region - DARK MODE
    def set_dark_mode(self, sett):
        """Apply dark or light palette and refresh the plot and icon."""
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
            self.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), "xview", "logo_dark.png")))
            # self.dark_mode_button.setText("Light mode")
            self.dark_mode_enabled = True
        else:
            self.setPalette(QApplication.style().standardPalette())
            self.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), "xview", "logo_light.png")))
            # self.dark_mode_button.setText("Dark mode")
            self.dark_mode_enabled = False

        self.update_plot()

        set_config_data("dark_mode", sett)

    def toggle_dark_mode(self):
        """Invert dark mode setting and apply it."""
        self.set_dark_mode(not get_config_file()["dark_mode"])
        # self.update_plot()
        # self.display_model_image()

    def finish_experiment(self):
        """Mark the current experiment as finished by writing its status file."""
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
        """Load or init the per-experiment JSON config and return it."""
        if not os.path.exists(os.path.join(self.experiments_dir, self.current_experiment_name, "config.json")):
            self.set_exp_config_file({})
        success = False
        while not success:
            try:
                config = json.load(open(os.path.join(self.experiments_dir, self.current_experiment_name, "config.json")))
                success = True
            except json.JSONDecodeError:
                print("Erreur de décodage JSON dans le fichier de configuration. On attend.")
        return config

    def get_exp_config_data(self, key):
        """Return a value from the per-experiment config by key (or None)."""
        return self.get_exp_config_file().get(key, None)

    def set_exp_config_file(self, config):
        """Write the full per-experiment config dict to disk."""
        with open(os.path.join(self.experiments_dir, self.current_experiment_name, "config.json"), "w") as f:
            json.dump(config, f, indent=4)

    def set_exp_config_data(self, key, value):
        """Update one key in the per-experiment config file."""
        config = self.get_exp_config_file()
        config[key] = value
        self.set_exp_config_file(config)

    # -----------------------------------------------------------------------------------------
    # region - PALETTE EDITOR
    def add_curve_color(self, color):
        """Append a color to curve palettes (light and dark coordinated)."""
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
        """Append a color to flag palettes (light and dark coordinated)."""
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

    # -----------------------------------------------------------------------------------------
    # region - REMOVE XP
    def remove_folders(self, folders):
        """Move selected experiment or group to Trash with a timestamp suffix."""
        from datetime import datetime
        from pathlib import Path

        # Trash path next to xview.log/config files (e.g., ~/.xview/Trash)
        try:
            base_dir = Path(log_file).parent  # log_file is defined at module init
        except Exception:
            base_dir = Path.home() / ".xview"
        trash_dir = base_dir / "Trash"
        trash_dir.mkdir(parents=True, exist_ok=True)

        ts = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")

        def move_to_trash(src_abs):
            """Move a file/dir to Trash with a timestamped name, handling potential collisions."""
            name = os.path.basename(src_abs.rstrip(os.sep))
            dest_base = f"{name}_{ts}"
            dest_path = trash_dir / dest_base
            suffix = 1
            # Avoid rare collisions if done within the same second
            while dest_path.exists():
                dest_path = trash_dir / f"{dest_base}_{suffix}"
                suffix += 1
            shutil.move(src_abs, str(dest_path))

        # If multiple entries provided, treat it as a group (folders[-1] is the group root)
        if len(folders) > 1:
            group_rel = folders[-1]
            group_abs = os.path.join(self.experiments_dir, group_rel)
            if os.path.exists(group_abs):
                # Reset selection if current exp is within this group
                if self.current_experiment_name and (
                    self.current_experiment_name == group_rel
                    or self.current_experiment_name.startswith(group_rel + os.sep)
                ):
                    self.current_experiment_name = None
                    self.current_scores = {}
                    self.current_flags = {}
                    self.current_train_loss = []
                    self.current_val_loss = []
                    self.update_plot()
                    self.exp_info_table.clearContents()
                move_to_trash(group_abs)
        else:
            # Single experiment
            path = folders[0]
            src_abs = os.path.join(self.experiments_dir, path)
            if os.path.exists(src_abs):
                if path == self.current_experiment_name:
                    self.current_experiment_name = None
                    self.current_scores = {}
                    self.current_flags = {}
                    self.current_train_loss = []
                    self.current_val_loss = []
                    self.update_plot()
                    self.exp_info_table.clearContents()
                move_to_trash(src_abs)

        self.update_experiment_list()

    # -----------------------------------------------------------------------------------------
    # region - MOVE XP
    def move_exp(self, path, new_group):
        """Move a selected experiment into a new or existing group."""
        new_path = os.path.join(new_group, path.split(os.sep)[-1])
        if os.path.exists(os.path.join(self.experiments_dir, path)):  #  si l exp existe
            if not os.path.exists(os.path.join(self.experiments_dir, new_group)):  # si le nouveau groupe n'existe pas
                os.makedirs(os.path.join(self.experiments_dir, new_group))
            shutil.move(os.path.join(self.experiments_dir, path), os.path.join(self.experiments_dir, new_group))

            self.update_experiment_list()
            if path == self.current_experiment_name:
                self.display_experiment(new_path)

    # -----------------------------------------------------------------------------------------
    # region - COPY XP
    def copy_exp(self, path, new_group):
        """Copy a selected experiment into another group; prompt on conflicts."""
        new_path = os.path.join(new_group, path.split(os.sep)[-1])
        if os.path.exists(os.path.join(self.experiments_dir, path)):  # si l'exp existe
            if not os.path.exists(os.path.join(self.experiments_dir, new_group)):  # si le nouveau groupe n'existe pas
                os.makedirs(os.path.join(self.experiments_dir, new_group))

            source_path = os.path.join(self.experiments_dir, path)
            dest_path = os.path.join(self.experiments_dir, new_path)

            # Vérifier si la destination existe déjà
            if os.path.exists(dest_path):
                exp_name = path.split(os.sep)[-1]
                reply = QMessageBox.question(
                    self,
                    "Conflit de nom",
                    f"L'expérience {exp_name} existe déjà dans le groupe {new_group}. Voulez-vous la remplacer ?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )

                if reply == QMessageBox.No:
                    return  # Annuler la copie

                # Supprimer la destination existante avant la copie
                if os.path.isdir(dest_path):
                    shutil.rmtree(dest_path)
                else:
                    os.remove(dest_path)

            # Utiliser copytree pour copier récursivement le dossier
            if os.path.isdir(source_path):
                shutil.copytree(source_path, dest_path)
            else:
                # Si c'est un fichier unique, utiliser copy2
                shutil.copy2(source_path, dest_path)

            self.update_experiment_list()

    # -----------------------------------------------------------------------------------------
    # region - SCREENSHOT
    def screenshot_graph(self):
        """Prend une capture d'écran du graphique."""
        if self.current_experiment_name:
            # Capture the matplotlib canvas directly (Qt5+ API)
            pixmap = self.canvas.grab()

            # Save to Linux clipboard (both Clipboard and Selection where available)
            clipboard = QApplication.clipboard()
            try:
                clipboard.setPixmap(pixmap, QClipboard.Clipboard)
                clipboard.setPixmap(pixmap, QClipboard.Selection)
            except Exception:
                # Fallback: set default mode only
                clipboard.setPixmap(pixmap)

            # If running under WSL2, also push the image to the Windows clipboard via PowerShell
            if self._in_wsl():
                try:
                    self._copy_pixmap_to_windows_clipboard(pixmap)
                    print("Screenshot copied to Windows clipboard (WSL).")
                except Exception as e:
                    print(f"WSL Windows clipboard fallback failed: {e}")

    def _in_wsl(self):
        """Detect if running under WSL/WSLg."""
        try:
            if os.environ.get("WSL_DISTRO_NAME"):
                return True
            return "microsoft" in platform.release().lower()
        except Exception:
            return False

    def _copy_pixmap_to_windows_clipboard(self, pixmap):
        """Save pixmap to a temp file and set the Windows clipboard image via PowerShell.

        Requires WSL with powershell.exe available. Uses wslpath to map the temp path.
        """
        # Save to a temporary PNG in WSL filesystem
        fd, tmp_path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        try:
            # Save pixmap to file
            pixmap.save(tmp_path, "PNG")

            # Convert WSL path to Windows path (e.g., /tmp/... -> C:\...)
            win_path = subprocess.check_output(["wslpath", "-w", tmp_path]).decode().strip()

            # Build PowerShell command to set image clipboard
            ps_cmd = (
                "Add-Type -AssemblyName System.Windows.Forms; "
                "Add-Type -AssemblyName System.Drawing; "
                f"$img=[System.Drawing.Image]::FromFile(\"{win_path}\"); "
                "[System.Windows.Forms.Clipboard]::SetImage($img)"
            )
            # Run in STA mode as required for Clipboard APIs
            subprocess.run([
                "powershell.exe",
                "-NoProfile",
                "-STA",
                "-Command",
                ps_cmd
            ], check=True)
        finally:
            # Clean up temp file
            try:
                os.remove(tmp_path)
            except Exception:
                pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    check_config_integrity()

    check_for_updates()

    curr_dir = os.path.abspath(os.path.dirname(__file__))

    viewer = ExperimentViewer()
    viewer.showMaximized()
    viewer.show()

    sys.exit(app.exec_())
