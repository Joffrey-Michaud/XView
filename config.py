"""XView configuration GUI to edit colors, styles, and folders.

Provides a PyQt5 window to manage palettes (light/dark), line styles, alpha,
and the experiments folder. Persists values in the XView config JSON.
"""

import sys
from PyQt5.QtWidgets import QApplication, QFileDialog, QWidget, QPushButton, QVBoxLayout, QSplitter, QGridLayout, QMainWindow, QHBoxLayout, QColorDialog, QComboBox, QLineEdit
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap, QIcon, QPalette, QColor
from PyQt5.QtCore import Qt, QDir
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from xview.utils.utils import compute_moving_average
import os
import numpy as np
from xview import get_config_file, set_config_file, set_config_data, config_exists, default_config


# ------------------------------------------------------------------ COLOR PICKER
# region - ColorPickerWidget
class ColorPickerWidget(QWidget):
    """Compact row of color buttons that opens a QColorDialog on click."""

    def __init__(self, colors=["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"], on_color_change=None):
        super().__init__()
        self.on_color_change = on_color_change
        self.layout = QHBoxLayout()
        self.color_buttons = []
        self.colors = colors

        # Couleurs de base
        base_colors = []
        for color in colors:
            base_colors.append(QColor(color))

        # Création des boutons de couleur
        for i, color in enumerate(colors):
            w = (400 - 50) // len(colors)
            qcolor = QColor(color)
            btn = QPushButton()
            btn.setFixedSize(w, w)
            btn.setStyleSheet(f"background-color: {qcolor.name()}; border: 1px solid black;")
            btn.clicked.connect(lambda _, idx=i: self.open_color_dialog(idx))
            self.color_buttons.append(btn)
            self.layout.addWidget(btn)

        self.setLayout(self.layout)

    def open_color_dialog(self, index):
        """Open color picker for the selected swatch and update callback."""
        sender = self.sender()
        current_color = sender.palette().button().color()
        color = QColorDialog.getColor(initial=current_color, parent=self)

        if color.isValid():
            sender.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
            self.colors[index] = color.name()  # Update internal color list

            if self.on_color_change:
                self.on_color_change(index, color.name())  # Call the callback

    def update_colors(self, colors):
        """Replace all swatch colors and refresh button styles."""
        self.colors = colors
        for btn, color in zip(self.color_buttons, colors):
            btn.setStyleSheet(f"background-color: {color}; border: 1px solid black;")


# ------------------------------------------------------------------ STYLE SETTER
# region - StyleSetter
class StyleSetter(QWidget):
    """Picker for Matplotlib line style and opacity (alpha)."""
    # widget pour choisir le style de ligne plt, et le alpha

    def __init__(self, ls, alpha, set_ls_callbak, set_alpha_callback):
        super().__init__()
        self.ls = ls
        self.alpha = alpha
        self.set_ls_callbak = set_ls_callbak
        self.set_alpha_callback = set_alpha_callback

        self.layout = QHBoxLayout()

        self.combo_box = QComboBox()
        self.combo_box.addItems([
            "Ligne continue (-)",
            "Tirets (--)",
            "Tiret-point (-.)",
            "Points (:)",
        ])
        # connect combo box to select_ls_callback
        self.combo_box.currentIndexChanged.connect(self.select_ls_callback)
        self.layout.addWidget(self.combo_box)

        style_map = {
            "-": 0,
            "--": 1,
            "-.": 2,
            ":": 3
        }

        self.inverted_style_map = {v: k for k, v in style_map.items()}

        if ls in style_map:
            self.combo_box.setCurrentIndex(style_map[ls])

        self.alpha_label = QLabel("Alpha :")
        self.alpha_input = QLineEdit()
        self.alpha_input.setPlaceholderText(f"{alpha}")
        # self.alpha_input.textChanged.connect(self.select_alpha_callback)
        self.alpha_input.editingFinished.connect(self.select_alpha_callback)

        self.layout.addWidget(self.alpha_label)
        self.layout.addWidget(self.alpha_input)

        self.setLayout(self.layout)

    def select_ls_callback(self, index):
        """Map combo index to matplotlib linestyle and notify parent."""
        self.set_ls_callbak(self.inverted_style_map[index])

    def select_alpha_callback(self):
        """Parse alpha input and notify parent setter."""
        alpha = self.alpha_input.text()
        self.set_alpha_callback(float(alpha))


# ------------------------------------------------------------------ CONFIG MANAGER
# region - ConfigManager
class ConfigManager(QMainWindow):
    """Standalone window to configure XView appearance and defaults."""

    def __init__(self):
        super().__init__()
        self.global_config = get_config_file()
        self.initUI()

    def initUI(self):
        """Build the UI and load current settings from the config file."""
        self.setWindowTitle("XView - Config")
        self.setWindowIcon(QIcon("logo_light.png"))
        self.setGeometry(300, 300, 1500, 750)

        self.dark_mode_enabled = False

        self.dark_mode_curves = self.get_color_theme("curves", dark_mode=True)
        self.dark_mode_flags = self.get_color_theme("flags", dark_mode=True)

        self.light_mode_curves = self.get_color_theme("curves", dark_mode=False)
        self.light_mode_flags = self.get_color_theme("flags", dark_mode=False)

        self.current_exp_folder = self.get_current_exps_folder()

        self.curves_ls, self.curves_alpha = self.get_curves_style()
        self.ma_curves_ls, self.ma_curves_alpha = self.get_ma_curves_style()
        self.flags_ls, self.flags_alpha = self.get_flags_style()
        self.interval = self.get_interval()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Layout principal avec QSplitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(splitter)

        left_widget = QWidget()
        left_widget.setFixedWidth(400)
        left_layout = QGridLayout()
        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)

        # figure widget
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        splitter.addWidget(self.canvas)

        layout = QVBoxLayout()

        # Create a label to display the logo
        logo_label = QLabel(self)
        pixmap = QPixmap('xview/logo_light.png')  # Replace with your logo path
        if not pixmap.isNull():
            pixmap = pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
        else:
            logo_label.setText("XView")
            logo_label.setStyleSheet("font-size: 24px; font-weight: bold;")
            logo_label.setAlignment(Qt.AlignCenter)

        left_layout.addWidget(logo_label, 0, 0)

        # ------------------------------------------------------------------------------------------
        # region - Exps folder
        self.exp_folder_label = QLabel(f"Current exps folder :\n{self.current_exp_folder}")
        self.exp_folder_label.setWordWrap(True)
        self.exp_folder_label.setStyleSheet("font-size: 15px;")
        self.exp_folder_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.exp_folder_label, 1, 0)

        exp_btn = QPushButton('Choose Exps Folder', self)
        exp_btn.clicked.connect(self.change_exp_folder)
        left_layout.addWidget(exp_btn, 2, 0)

        # ------------------------------------------------------------------------------------------
        # region - upd interval
        self.inteval_widget = QWidget()
        self.interval_layout = QHBoxLayout()

        self.interval_label = QLabel("Graph update interval (s) :")
        self.interval_input = QLineEdit()
        self.interval_layout.addWidget(self.interval_label)
        self.interval_layout.addWidget(self.interval_input)
        self.inteval_widget.setLayout(self.interval_layout)

        self.interval_input.setPlaceholderText(f"{self.interval}")
        self.interval_input.editingFinished.connect(self.set_interval)
        left_layout.addWidget(self.inteval_widget, 3, 0)

        self.dark_mode_btn = QPushButton('Dark Mode', self)
        self.dark_mode_btn.clicked.connect(self.toggle_dark_mode)
        left_layout.addWidget(self.dark_mode_btn, 4, 0)
        # self.setLayout(layout)

        # ------------------------------------------------------------------------------------------
        # region - Colors and styles

        # ----------------------------------------------------------- CURVES
        # section_label = QLabel("Choose the colors of the curves")
        section_label = QLabel("Choose the style of the curves")
        section_label.setStyleSheet("font-size: 15px;")
        section_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(section_label, 5, 0)

        self.color_widget = ColorPickerWidget(colors=self.light_mode_curves, on_color_change=self.update_curves_colors)
        left_layout.addWidget(self.color_widget, 6, 0)

        self.curves_style_setter = StyleSetter(self.curves_ls, self.curves_alpha,
                                               set_ls_callbak=self.set_curves_ls,
                                               set_alpha_callback=self.set_curves_alpha)
        left_layout.addWidget(self.curves_style_setter, 7, 0)

        # ----------------------------------------------------------- MA CURVES
        self.ma_label = QLabel("Choose the style of the moving average curves")
        self.ma_label.setStyleSheet("font-size: 15px;")
        self.ma_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.ma_label, 8, 0)

        self.ma_curves_style_setter = StyleSetter(self.ma_curves_ls, self.ma_curves_alpha,
                                                  set_ls_callbak=self.set_ma_curves_ls,
                                                  set_alpha_callback=self.set_ma_curves_alpha)
        left_layout.addWidget(self.ma_curves_style_setter, 9, 0)

        # ----------------------------------------------------------- FLAGS
        section_label_2 = QLabel("Choose the style of the flags")
        section_label_2.setStyleSheet("font-size: 15px;")
        section_label_2.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(section_label_2, 10, 0)

        self.color_widget_2 = ColorPickerWidget(colors=self.light_mode_flags, on_color_change=self.update_flags_colors)
        left_layout.addWidget(self.color_widget_2, 11, 0)

        self.flags_style_setter = StyleSetter(self.flags_ls, self.flags_alpha,
                                              set_ls_callbak=self.set_flags_ls,
                                              set_alpha_callback=self.set_flags_alpha)
        left_layout.addWidget(self.flags_style_setter, 12, 0)

        # region - save button
        # save_btn = QPushButton('Save')
        # save_btn.clicked.connect(self.save_config)
        # left_layout.addWidget(save_btn, 13, 0)

        self.plot_example()

        self.set_dark_mode(self.global_config["dark_mode"])

        self.show()

    def change_exp_folder(self):
        """Prompt user to pick the experiments folder and persist it."""

        dialog = QFileDialog(self, 'Select Folder')
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOptions(QFileDialog.ShowDirsOnly | QFileDialog.DontUseNativeDialog)
        dialog.setFilter(dialog.filter() | QDir.Hidden)

        if dialog.exec_():
            folder_path = dialog.selectedFiles()[0]
        else:
            folder_path = None

        if folder_path:
            self.current_exp_folder = folder_path
            self.exp_folder_label.setText(f"Current exps folder :\n{self.current_exp_folder}")
            set_config_data('data_folder', folder_path)

    # region - plot_example
    def plot_example(self):
        """Render a small demo plot using the current palette and styles."""
        if self.dark_mode_enabled:
            curves_colors = self.dark_mode_curves
            flags_colors = self.dark_mode_flags
        else:
            curves_colors = self.light_mode_curves
            flags_colors = self.light_mode_flags

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

        x = np.linspace(0, 2 * np.pi, 200)
        amplitudes = [1, 2, 0.5, 1.5, 0.8]
        for i, (color, amp) in enumerate(zip(curves_colors, amplitudes)):
            y = amp * np.sin(x + i) + np.random.normal(0, 0.05, len(x))
            ax.plot(x, y, color=color, label=f"Curve {i + 1}", ls=self.curves_ls, alpha=self.curves_alpha)

            ax.plot(x, compute_moving_average(y, 10), color=color, label=f"MA Curve {i + 1}", ls=self.ma_curves_ls, alpha=self.ma_curves_alpha)

        coords = np.linspace(0, 2 * np.pi, 5)
        for i, (color, x) in enumerate(zip(flags_colors, coords[1:-1])):
            y = amp * np.sin(x + i)
            ax.axvline(x, color=color, label=f"Flag {i + 1}", ls=self.flags_ls, alpha=self.flags_alpha)

        # x = np.linspace(0, 2 * np.pi, 200)
        # for i, color in enumerate(curves_colors):
        #     y = np.sin(x + i)
        #     ax.plot(x, y, color=color, label=f"Sin {i+1}")

        ax.legend(facecolor=bg_color, edgecolor=text_color, labelcolor=text_color)

        ax.set_title("Example Plot")
        ax.set_xlabel("X-axis")
        ax.set_ylabel("Y-axis")
        self.canvas.draw()

    def set_dark_mode(self, dark_mode):
        """Switch between dark/light palettes and update preview plot."""
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

            self.color_widget.update_colors(self.dark_mode_curves)
            self.color_widget_2.update_colors(self.dark_mode_flags)

            self.setPalette(dark_palette)
            self.dark_mode_enabled = True

            self.setWindowIcon(QIcon("logo_dark.png"))
            self.dark_mode_btn.setText("Light mode")
        else:
            self.setPalette(QApplication.style().standardPalette())
            self.color_widget.update_colors(self.light_mode_curves)
            self.color_widget_2.update_colors(self.light_mode_flags)
            self.dark_mode_enabled = False
            self.setWindowIcon(QIcon("logo_light.png"))
            self.dark_mode_btn.setText("Dark mode")

        self.plot_example()
        set_config_data('dark_mode', dark_mode)

    def toggle_dark_mode(self):
        """Invert the dark mode toggle and apply."""
        self.set_dark_mode(not self.dark_mode_enabled)

    def get_color_theme(self, color_section="curves", dark_mode=False):
        """Return list of colors for curves or flags in given mode."""
        config = get_config_file()
        if color_section == "curves":
            if dark_mode:
                return config.get("dark_mode_curves", ["#A2D2DF", "#F6EFBD", "#E4C087", "#BC7C7C", "#FF00FF"])
            else:
                return config.get("light_mode_curves", ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"])
        elif color_section == "flags":
            if dark_mode:
                return config.get("dark_mode_flags", ["#fafafa", "#fafafa", "#fafafa"])
            else:
                return config.get("light_mode_flags", ["#000000", "#000000", "#000000"])

    def get_curves_style(self):
        """Read curves linestyle and alpha from config."""
        config = get_config_file()
        return config["curves_ls"], config["curves_alpha"]

    def get_ma_curves_style(self):
        """Read moving-average linestyle and alpha from config."""
        config = get_config_file()
        return config["ma_curves_ls"], config["ma_curves_alpha"]

    def get_flags_style(self):
        """Read flags linestyle and alpha from config."""
        config = get_config_file()
        return config["flags_ls"], config["flags_alpha"]

    def get_interval(self):
        """Return graph update interval (seconds)."""
        config = get_config_file()
        return config["update_interval"]

    def set_interval(self):
        """Persist update interval from the input field and refresh preview."""
        interval = self.interval_input.text()
        self.interval = float(interval)
        set_config_data('update_interval', self.interval)

    def set_curves_ls(self, ls):
        """Update curves linestyle and refresh preview plot."""
        self.curves_ls = ls
        set_config_data('curves_ls', ls)
        self.plot_example()

    def set_ma_curves_ls(self, ls):
        """Update moving-average linestyle and refresh preview plot."""
        self.ma_curves_ls = ls
        set_config_data('ma_curves_ls', ls)
        self.plot_example()

    def set_flags_ls(self, ls):
        """Update flags linestyle and refresh preview plot."""
        self.flags_ls = ls
        set_config_data('flags_ls', ls)
        self.plot_example()

    def set_curves_alpha(self, alpha):
        """Update curves opacity and refresh preview plot."""
        self.curves_alpha = alpha
        set_config_data('curves_alpha', alpha)
        self.plot_example()

    def set_ma_curves_alpha(self, alpha):
        """Update moving-average opacity and refresh preview plot."""
        self.ma_curves_alpha = alpha
        set_config_data('ma_curves_alpha', alpha)
        self.plot_example()

    def set_flags_alpha(self, alpha):
        """Update flags opacity and refresh preview plot."""
        self.flags_alpha = alpha
        set_config_data('flags_alpha', alpha)
        self.plot_example()

    def get_current_exps_folder(self):
        """Return the current experiments root folder from config."""
        config = get_config_file()
        return config["data_folder"]

    def update_curves_colors(self, index, new_color):
        """Persist a color change for curves (light or dark mode)."""
        if self.dark_mode_enabled:
            self.dark_mode_curves[index] = new_color
            set_config_data('dark_mode_curves', self.dark_mode_curves)
        else:
            self.light_mode_curves[index] = new_color
            set_config_data('light_mode_curves', self.light_mode_curves)

        self.plot_example()

    def update_flags_colors(self, index, new_color):
        """Persist a color change for flags (light or dark mode)."""
        if self.dark_mode_enabled:
            self.dark_mode_flags[index] = new_color
            set_config_data('dark_mode_flags', self.dark_mode_flags)
        else:
            self.light_mode_flags[index] = new_color
            set_config_data('light_mode_flags', self.light_mode_flags)

        self.plot_example()


if __name__ == '__main__':
    if not config_exists():
        data_folder = os.path.dirname(f"{os.path.expanduser('~')}/.xview/exps/")
        default_config["data_folder"] = data_folder
        # default_config = {
        #     "data_folder": data_folder,
        #     "dark_mode_curves": ["#A2D2DF", "#F6EFBD", "#E4C087", "#BC7C7C", "#FF00FF"],
        #     "dark_mode_flags": ["#fafafa", "#fafafa", "#fafafa"],
        #     "light_mode_curves": ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"],
        #     "light_mode_flags": ["#000000", "#000000", "#000000"],
        #     "curves_ls": "-",
        #     "curves_alpha": 1.0,
        #     "flags_ls": "-",
        #     "flags_alpha": 1.0,
        #     "ma_curves_ls": "--",
        #     "ma_curves_alpha": 0.5,
        #     "update_interval": 60,
        #     "dark_mode": False,
        #     "remind_me_later_date": None,
        #     "first_since_update": False,
        #     "auto_update": False
        # }
        set_config_file(default_config)
        if not os.path.exists(data_folder):
            os.makedirs(data_folder, exist_ok=True)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    ex = ConfigManager()
    sys.exit(app.exec_())
