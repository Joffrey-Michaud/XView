import sys
from PyQt5.QtWidgets import QScrollArea, QApplication, QWidget, QPushButton, QVBoxLayout, QSplitter, QGridLayout, QMainWindow, QHBoxLayout, QComboBox, QLabel, QCheckBox, QDialog
from PyQt5.QtGui import QIcon, QPalette, QColor, QClipboard
from PyQt5.QtCore import Qt, QDateTime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from xview import get_config_data
import os
from xview.compare_utils import get_metrics
import numpy as np
import subprocess
import tempfile
import platform


# classe qui contient des lignes de type : checkbox puis label contenant le nom de l'exp cote à cote.
# doit avoir une méthode pour ajouter des expériences, une méthode pour enlever toutes les lignes, une méthodes pour savoir quelles sont les expériences cochées
class ExperimentPanel(QWidget):
    def __init__(self, update_plot_callback):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.update_plot_callback = update_plot_callback

    def add_experiment(self, exp_name):
        h_layout = QHBoxLayout()
        checkbox = QCheckBox()
        checkbox.setChecked(True)
        checkbox.stateChanged.connect(self.update_plot_callback)
        label = QLabel(exp_name)
        label.setAlignment(Qt.AlignLeft)
        h_layout.addWidget(checkbox)
        h_layout.addWidget(label)
        h_layout.addStretch()
        self.layout.addLayout(h_layout)

    def clear_experiments(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                child_layout = item.layout()
                if child_layout is not None:
                    self._clear_layout(child_layout)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                child_layout = item.layout()
                if child_layout is not None:
                    self._clear_layout(child_layout)


    def get_checked_experiments(self):
        checked_exps = []
        for i in range(self.layout.count()):
            h_layout = self.layout.itemAt(i)
            checkbox = h_layout.itemAt(0).widget()
            label = h_layout.itemAt(1).widget()
            if checkbox.isChecked():
                checked_exps.append(label.text())

        return checked_exps

# ------------------------------------------------------------------ COMPARISON WINDOW
# region - ComparisonWindow
# class ComparisonWindow(QMainWindow):
class ComparisonWindow(QDialog):
    def __init__(self, group_path):
        super().__init__()
        
        self.group_path = group_path
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Comparison Window")
        self.setGeometry(100, 100, 920, 600)
        self.setWindowIcon(QIcon("logo_light.png"))

        self.dark_mode_enabled = get_config_data("dark_mode")

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.metrics = None

        # Définition du widget de gauche
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout()
        self.left_panel.setFixedWidth(220)
        self.left_panel.setLayout(self.left_layout)
        layout.addWidget(self.left_panel)

        # On remplit le widget de gauche
        self.group_label = QLabel("Group:")
        self.left_layout.addWidget(self.group_label)

        # Widget pour sélectionner la métrique (label + menu déroulant cote à cote)
        self.metric_widget = QWidget()
        self.metric_layout = QHBoxLayout()
        self.metric_widget.setLayout(self.metric_layout)
        self.left_layout.addWidget(self.metric_widget)

        self.metric_label = QLabel("Metric:")
        self.metric_layout.addWidget(self.metric_label)

        self.metric_combo = QComboBox()
        self.metric_layout.addWidget(self.metric_combo)
        self.metric_combo.currentIndexChanged.connect(self.update_plot)

        # Widget pour sélectionner si on veut checker le min ou le max
        self.min_max_widget = QWidget()
        self.min_max_layout = QHBoxLayout()
        self.min_max_widget.setLayout(self.min_max_layout)
        self.left_layout.addWidget(self.min_max_widget)

        self.min_max_label = QLabel("Min/Max:")
        self.min_max_layout.addWidget(self.min_max_label)

        self.min_max_combo = QComboBox()
        self.min_max_layout.addWidget(self.min_max_combo)
        self.min_max_combo.addItem("Min")
        self.min_max_combo.addItem("Max")
        self.min_max_combo.currentIndexChanged.connect(self.update_plot)

        # Bouton Save
        self.save_button = QPushButton("Save")
        self.left_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_graph)

        # Bouton screenshot
        self.screenshot_button = QPushButton("Screenshot")
        self.left_layout.addWidget(self.screenshot_button)
        self.screenshot_button.clicked.connect(self.screenshot_graph)

        # Experiment panel
        self.exp_panel = ExperimentPanel(update_plot_callback=self.update_plot)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.exp_panel)
        self.left_layout.addWidget(self.scroll_area)

        self.left_layout.addStretch()

        # Widget de droite : affichage du graphe
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.mpl_connect("resize_event", self._on_resize)
        layout.addWidget(self.canvas)

        # Add your UI elements here
        self.update_window(self.group_path)

        self.set_dark_mode(get_config_data('dark_mode'))
        self.show()

    def _on_resize(self, event):
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def update_window(self, group_path):
        self.group_path = group_path
        self.group_label.setText(f"Group : {self.group_path}")

        self.exp_panel.clear_experiments()

        # lister les experiences du groupe
        experiments_folder = get_config_data(key="data_folder")
        group_folder = os.path.join(experiments_folder, self.group_path)
        exps = os.listdir(group_folder)
        # garder uniquement les dossiers
        exps = [d for d in sorted(exps) if os.path.isdir(os.path.join(group_folder, d))]

        for exp in exps:
            self.exp_panel.add_experiment(exp)
            exp_folder = os.path.join(group_folder, exp)
            if os.path.isdir(exp_folder):
                metrics = get_metrics(exp_folder)
                # on met à jour les valeurs de la combobox

        # garder uniquement les valeurs uniques de metrics
        self.metrics = sorted(list(set(metrics)))

        self.metric_combo.clear()
        self.metric_combo.addItems(self.metrics)

        self.metric_combo.setCurrentIndex(0)

        self.update_plot()

    @staticmethod
    def read_scores(file_path):
        """Lit les scores à partir d'un fichier et retourne une liste de tuples (x, y)."""
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                lines = f.readlines()
            y = []
            for line in lines:
                values = line.strip().split(",")
                if len(values) == 1:
                    y.append(float(values[0]))
                else:
                    y.append(float(values[1]))
            return y

        else:
            print(f"Le fichier {file_path} n'existe pas.")
            return []

    # region - update plot
    def update_plot(self):
        selected_metric = self.metric_combo.currentText()
        min_max = "min" if self.min_max_combo.currentIndex() == 0 else "max"

        experiments_folder = get_config_data(key="data_folder")
        group_folder = os.path.join(experiments_folder, self.group_path)

        exps = self.exp_panel.get_checked_experiments()
        if len(exps) > 0:
            best_scores = []

            for exp in exps:
                scores_folder = os.path.join(group_folder, exp, "scores")
                if os.path.exists(os.path.join(scores_folder, f"{selected_metric}.txt")):
                    score = self.read_scores(os.path.join(scores_folder, f"{selected_metric}.txt"))
                    best_scores.append(np.min(score) if min_max == "min" else np.max(score))

            if best_scores:
                # trier les scores par ordre croissant en les gardant alignés avec le nom de l'exp
                sorted_scores, sorted_exps = zip(*sorted(zip(best_scores, exps), key=lambda x: x[0]))

                self.figure.clear()
                ax = self.figure.add_subplot(111)
                # self.figure.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.1)

                if self.dark_mode_enabled:
                    bg_color = "#191919"
                    text_color = "white"
                    bar_color = "deepskyblue"

                else:
                    bg_color = "white"
                    text_color = "black"
                    bar_color = "skyblue"

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

                bars = ax.barh(sorted_exps, sorted_scores, color=[bar_color] * len(sorted_exps))

                # -- Ajuste l’axe X
                max_score = max(sorted_scores)
                ax.set_xlim(0, max_score * 1.05)

                # -- Texte
                threshold = 0.15 * max_score      # 15 % du score max
                for bar, score in zip(bars, sorted_scores):
                    y_center = bar.get_y() + bar.get_height() / 2
                    if score >= threshold:                     # texte à l’intérieur
                        x_text = score - 0.02 * max_score      # petit retrait vers la gauche
                        ax.text(x_text, y_center, f"{score:.4f}",
                                va="center", ha="right", color="white", fontsize=9)
                    else:                                      # texte à l’extérieur
                        x_text = score + 0.01 * max_score
                        ax.text(x_text, y_center, f"{score:.4f}",
                                va="center", ha="left", color="white" if self.dark_mode_enabled else "black", fontsize=9)
                ax.set_xlabel(f"{selected_metric}")
                ax.set_ylabel("Experiments")
                ax.set_title(f"Group : {self.group_path} - Metric : {selected_metric}")
                ax.grid(axis="x")
                self.canvas.draw()
        else:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            self.canvas.draw()

    def set_dark_mode(self, dark_mode):
        if dark_mode:
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

            self.setWindowIcon(QIcon("logo_dark.png"))
        else:
            self.setPalette(QApplication.style().standardPalette())
            self.setWindowIcon(QIcon("logo_light.png"))
        
        self.dark_mode_enabled = get_config_data("dark_mode")
        self.update_plot()
    
    # region - SCREENSHOT
    def screenshot_graph(self):
        """Prend une capture d'écran du graphique."""
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
    
    # region - SAVE
    def save_graph(self):
        """Enregistre le graphe actuel dans le dossier de l'expérience sélectionnée."""
        experiments_folder = get_config_data(key="data_folder")
        group_folder = os.path.join(experiments_folder, self.group_path)

        # format yyyy-mm-dd_HH-MM-SS
        figure_date = QDateTime.currentDateTime().toString("yyyy-MM-dd_HH-mm-ss")

        save_path = os.path.join(group_folder, f"compare_{self.metric_combo.currentText()}_{figure_date}.png")

        self.figure.savefig(save_path, dpi=300)  # Enregistrer en haute qualité
        print(f"Graph enregistré dans : {save_path}")

