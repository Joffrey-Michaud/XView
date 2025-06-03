import sys
from PyQt5.QtWidgets import QApplication, QFileDialog, QWidget, QPushButton, QVBoxLayout, QSplitter, QGridLayout, QMainWindow, QHBoxLayout, QColorDialog, QComboBox, QLineEdit
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap, QIcon, QPalette, QColor
from PyQt5.QtCore import Qt, QDir
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from xview.utils.utils import write_json, read_json, compute_moving_average
import os
import numpy as np
import time
from xview.update.update_project import warn_if_outdated
from xview import get_config_file, set_config_file, set_config_data, config_exists


# ------------------------------------------------------------------ COLOR PICKER
# region - ColorPickerWidget
class ColorPickerWidget(QWidget):
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
            # w = (400 - 50) // len(colors)
            w = 25
            qcolor = QColor(color)
            btn = QPushButton()
            btn.setFixedSize(w, w)
            btn.setStyleSheet(f"background-color: {qcolor.name()}; border: 1px solid black;")
            btn.clicked.connect(lambda _, idx=i: self.open_color_dialog(idx))
            self.color_buttons.append(btn)
            self.layout.addWidget(btn)

        self.setLayout(self.layout)

    def open_color_dialog(self, index):
        sender = self.sender()
        current_color = sender.palette().button().color()
        color = QColorDialog.getColor(initial=current_color, parent=self)

        if color.isValid():
            sender.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
            self.colors[index] = color.name()  # Update internal color list

            if self.on_color_change:
                self.on_color_change(index, color.name())  # Call the callback

    def update_colors(self, colors):
        self.colors = colors
        for btn, color in zip(self.color_buttons, colors):
            btn.setStyleSheet(f"background-color: {color}; border: 1px solid black;")


# ------------------------------------------------------------------ STYLE SETTER
# region - StyleSetter
class StyleSetter(QWidget):
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
        self.set_ls_callbak(self.inverted_style_map[index])

    def select_alpha_callback(self):
        alpha = self.alpha_input.text()
        self.set_alpha_callback(float(alpha))


# ------------------------------------------------------------------ SETTINGS DISPLAY
# region - DisplaySettings
class DisplaySettings(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.global_config = get_config_file()
        self.dark_mode_enabled = get_config_file()["dark_mode"]

        self.dark_mode_curves = self.get_color_theme("curves", dark_mode=True)
        self.dark_mode_flags = self.get_color_theme("flags", dark_mode=True)

        self.light_mode_curves = self.get_color_theme("curves", dark_mode=False)
        self.light_mode_flags = self.get_color_theme("flags", dark_mode=False)

        self.curves_ls, self.curves_alpha = self.get_curves_style()
        self.ma_curves_ls, self.ma_curves_alpha = self.get_ma_curves_style()
        self.flags_ls, self.flags_alpha = self.get_flags_style()

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        self.splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)

        # region - left widget
        self.left_widget = QWidget()
        self.left_widget.setFixedWidth(250)
        self.left_layout = QVBoxLayout()
        self.left_widget.setLayout(self.left_layout)
        self.splitter.addWidget(self.left_widget)

        # region - figure widget
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.splitter.addWidget(self.canvas)

        self.logo_label = QLabel(self)
        pixmap = QPixmap('xview/logo_light.png')  # Replace with your logo path
        pixmap = pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.left_layout.addWidget(self.logo_label)

        # region - DM BUTTON
        self.dark_mode_btn = QPushButton('Dark Mode', self)
        self.dark_mode_btn.clicked.connect(self.toggle_dark_mode)
        self.left_layout.addWidget(self.dark_mode_btn)

        # ------------------------------------------------------------------------------------------
        # region - Colors and styles

        # ----------------------------------------------------------- CURVES
        # section_label = QLabel("Choose the colors of the curves")
        section_label = QLabel("Choose the style of the curves")
        # section_label.setStyleSheet("font-size: 10px;")
        section_label.setAlignment(Qt.AlignCenter)
        self.left_layout.addWidget(section_label)

        self.color_widget = ColorPickerWidget(colors=self.light_mode_curves, on_color_change=self.update_curves_colors)
        self.left_layout.addWidget(self.color_widget)

        self.curves_style_setter = StyleSetter(self.curves_ls, self.curves_alpha,
                                               set_ls_callbak=self.set_curves_ls,
                                               set_alpha_callback=self.set_curves_alpha)
        self.left_layout.addWidget(self.curves_style_setter)

        # ----------------------------------------------------------- MA CURVES
        self.ma_label = QLabel("Choose the style of the moving average curves")
        # self.ma_label.setStyleSheet("font-size: 10px;")
        self.ma_label.setAlignment(Qt.AlignCenter)
        self.left_layout.addWidget(self.ma_label)

        self.ma_curves_style_setter = StyleSetter(self.ma_curves_ls, self.ma_curves_alpha,
                                                  set_ls_callbak=self.set_ma_curves_ls,
                                                  set_alpha_callback=self.set_ma_curves_alpha)
        self.left_layout.addWidget(self.ma_curves_style_setter)

        # ----------------------------------------------------------- FLAGS
        section_label_2 = QLabel("Choose the style of the flags")
        # section_label_2.setStyleSheet("font-size: 10px;")
        section_label_2.setAlignment(Qt.AlignCenter)
        self.left_layout.addWidget(section_label_2)

        self.color_widget_2 = ColorPickerWidget(colors=self.light_mode_flags, on_color_change=self.update_flags_colors)
        self.left_layout.addWidget(self.color_widget_2)

        self.flags_style_setter = StyleSetter(self.flags_ls, self.flags_alpha,
                                              set_ls_callbak=self.set_flags_ls,
                                              set_alpha_callback=self.set_flags_alpha)
        self.left_layout.addWidget(self.flags_style_setter)

        # region - save button
        # save_btn = QPushButton('Save')
        # save_btn.clicked.connect(self.save_config)
        # left_layout.addWidget(save_btn, 13, 0)

        self.plot_example()

        self.set_dark_mode(self.global_config["dark_mode"])

        self.show()

    # region - plot_example
    def plot_example(self):
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

            pixmap = QPixmap('xview/logo_dark.png')  # Replace with your logo path
            pixmap = pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)

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

            pixmap = QPixmap('xview/logo_light.png')  # Replace with your logo path
            pixmap = pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)

        self.plot_example()
        set_config_data('dark_mode', dark_mode)

    def toggle_dark_mode(self):
        self.set_dark_mode(not self.dark_mode_enabled)
        self.parent.set_dark_mode(self.dark_mode_enabled)  # Notify parent if needed

    def get_color_theme(self, color_section="curves", dark_mode=False):
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
        config = get_config_file()
        return config["curves_ls"], config["curves_alpha"]

    def get_ma_curves_style(self):
        config = get_config_file()
        return config["ma_curves_ls"], config["ma_curves_alpha"]

    def get_flags_style(self):
        config = get_config_file()
        return config["flags_ls"], config["flags_alpha"]

    def set_curves_ls(self, ls):
        self.curves_ls = ls
        set_config_data('curves_ls', ls)
        self.plot_example()

    def set_ma_curves_ls(self, ls):
        self.ma_curves_ls = ls
        set_config_data('ma_curves_ls', ls)
        self.plot_example()

    def set_flags_ls(self, ls):
        self.flags_ls = ls
        set_config_data('flags_ls', ls)
        self.plot_example()

    def set_curves_alpha(self, alpha):
        self.curves_alpha = alpha
        set_config_data('curves_alpha', alpha)
        self.plot_example()

    def set_ma_curves_alpha(self, alpha):
        self.ma_curves_alpha = alpha
        set_config_data('ma_curves_alpha', alpha)
        self.plot_example()

    def set_flags_alpha(self, alpha):
        self.flags_alpha = alpha
        set_config_data('flags_alpha', alpha)
        self.plot_example()

    def update_curves_colors(self, index, new_color):
        if self.dark_mode_enabled:
            self.dark_mode_curves[index] = new_color
            set_config_data('dark_mode_curves', self.dark_mode_curves)
        else:
            self.light_mode_curves[index] = new_color
            set_config_data('light_mode_curves', self.light_mode_curves)

        self.plot_example()

    def update_flags_colors(self, index, new_color):
        if self.dark_mode_enabled:
            self.dark_mode_flags[index] = new_color
            set_config_data('dark_mode_flags', self.dark_mode_flags)
        else:
            self.light_mode_flags[index] = new_color
            set_config_data('light_mode_flags', self.light_mode_flags)

        self.plot_example()
