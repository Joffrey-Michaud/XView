from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QColorDialog, QComboBox, QLineEdit, QSplitter, QHBoxLayout, QMenu, QInputDialog, QDialog
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap, QIcon, QPalette, QColor
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from xview.utils.utils import compute_moving_average
import numpy as np
from xview import get_config_file, set_config_data, get_config_data
import time

# ------------------------------------------------------------------------- ColorPickerWidget
# region - COLOR PICKER
class ColorPickerWidget(QWidget):
    def __init__(self, palette, type, update_plot_ex=None):
        super().__init__()
        assert type in ["curve", "flag"], "Type must be either 'curve' or 'flag'."
        self.type = type
        self.palette = palette
        self.dark_mode_enabled = get_config_file()["dark_mode"]
        self.update_plot_ex = update_plot_ex
        self.color_buttons = []

        self.layout = QHBoxLayout()

        self.add_btn = QPushButton("+")
        self.add_btn.setFixedSize(20, 20)
        self.add_btn.clicked.connect(self.add_color_click)

        self.init_btns()

        self.setLayout(self.layout)

    # region - add
    def add_color_click(self):
        new_color = QColorDialog.getColor(parent=self)  #  sélectionner une couleur
        if new_color.isValid():
            new_color_name = new_color.name()
            if self.type == "curve":
                self.palette.add_curve_color(new_color_name)  #  ajouter la couleur à la palette et réécrire config file
            elif self.type == "flag":
                self.palette.add_flag_color(new_color_name)
            # Supprimer les anciens boutons de l'interface
            self.reset_buttons()
            self.update_plot_ex()  # Mettre à jour le graphique si nécessaire

    def get_colors(self):
        if self.type == "curve":
            return self.palette.light_mode_curves if not self.dark_mode_enabled else self.palette.dark_mode_curves
        elif self.type == "flag":
            return self.palette.light_mode_flags if not self.dark_mode_enabled else self.palette.dark_mode_flags

    # region - init btns
    def init_btns(self):
        colors = self.get_colors()
        for i, color in enumerate(colors):
            btn = QPushButton()
            btn.setFixedSize(25, 25)
            btn.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
            # click gauche : modifier la couleur
            btn.clicked.connect(lambda _, idx=i: self.open_color_dialog(idx))
            # click droit : supprimer la couleur
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
            btn.customContextMenuRequested.connect(
                lambda pos, idx=i, b=btn: self.show_context_menu(pos, idx, b)
            )
            self.color_buttons.append(btn)
            self.layout.addWidget(btn)
        self.layout.addWidget(self.add_btn)

    def reset_buttons(self):
        for btn in self.color_buttons:
            self.layout.removeWidget(btn)
            btn.deleteLater()  # Nettoyage mémoire

        # Vider la liste des boutons
        self.color_buttons.clear()
        self.init_btns()

    # region - left click
    def open_color_dialog(self, index):
        sender = self.sender()
        current_color = sender.palette().button().color()
        color = QColorDialog.getColor(initial=current_color, parent=self)

        if color.isValid():
            sender.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
            if self.type == "curve":
                if not self.dark_mode_enabled:
                    self.palette.light_mode_curves[index] = color.name()
                else:
                    self.palette.dark_mode_curves[index] = color.name()
            elif self.type == "flag":
                if not self.dark_mode_enabled:
                    self.palette.light_mode_flags[index] = color.name()
                else:
                    self.palette.dark_mode_flags[index] = color.name()

            self.palette.set_config_palette()  # Mettre à jour la configuration de la palette
        self.update_plot_ex()

    # region - right click
    def show_context_menu(self, pos, index, button):
        context_menu = QMenu(self)
        change_action = context_menu.addAction("Change")
        remove_action = context_menu.addAction("Remove")
        global_pos = button.mapToGlobal(pos)
        action = context_menu.exec_(global_pos)

        if action == change_action:
            self.open_color_dialog(index)

        if action == remove_action:
            if self.type == "curve":
                self.palette.rm_curve_color(index)
            elif self.type == "flag":
                self.palette.rm_flag_color(index)
            self.reset_buttons()
            self.update_plot_ex()  # Mettre à jour le graphique si nécessaire

    def update_colors(self):
        self.dark_mode_enabled = get_config_file()["dark_mode"]
        colors = self.get_colors()
        for btn, color in zip(self.color_buttons, colors):
            btn.setStyleSheet(f"background-color: {color}; border: 1px solid black;")


# ------------------------------------------------------------------------- StyleSetter
# region - STYLE SETTER
class StyleSetter(QWidget):
    def __init__(self, palette, type, update_plot_ex=None):
        super().__init__()
        assert type in ["curve", "ma_curve", "flag"], "Type must be either 'curve' or 'flag'."
        self.type = type
        self.palette = palette
        self.update_plot_ex = update_plot_ex

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

        self.style_map = {
            "-": 0,
            "--": 1,
            "-.": 2,
            ":": 3
        }
        self.inverted_style_map = {v: k for k, v in self.style_map.items()}

        self.alpha_label = QLabel("Alpha :")
        self.alpha_input = QLineEdit()
        self.alpha_input.setPlaceholderText(f"{self.get_alpha()}")
        self.alpha_input.editingFinished.connect(self.select_alpha_callback)

        self.layout.addWidget(self.alpha_label)
        self.layout.addWidget(self.alpha_input)

        self.init_values()

        self.setLayout(self.layout)

    def init_values(self):
        self.combo_box.setCurrentIndex(self.style_map[self.get_ls()])
        self.alpha_input.setText(str(self.get_alpha()))

    def select_ls_callback(self, index):
        self.set_ls(self.inverted_style_map[index])
        self.update_plot_ex()

    def select_alpha_callback(self):
        alpha = self.alpha_input.text()
        self.set_alpha(float(alpha))
        self.update_plot_ex()

    # region - get/set ls/alpha
    def get_ls(self):
        if self.type == "curve":
            return self.palette.curves_ls
        elif self.type == "ma_curve":
            return self.palette.ma_curves_ls
        elif self.type == "flag":
            return self.palette.flags_ls

    def get_alpha(self):
        if self.type == "curve":
            return self.palette.curves_alpha
        elif self.type == "ma_curve":
            return self.palette.ma_curves_alpha
        elif self.type == "flag":
            return self.palette.flags_alpha

    def set_ls(self, ls):
        if self.type == "curve":
            self.palette.curves_ls = ls
        elif self.type == "ma_curve":
            self.palette.ma_curves_ls = ls
        elif self.type == "flag":
            self.palette.flags_ls = ls
        self.palette.set_config_palette()

    def set_alpha(self, alpha):
        if self.type == "curve":
            self.palette.curves_alpha = alpha
        elif self.type == "ma_curve":
            self.palette.ma_curves_alpha = alpha
        elif self.type == "flag":
            self.palette.flags_alpha = alpha
        self.palette.set_config_palette()

# ------------------------------------------------------------------ SETTINGS DISPLAY
# region - DisplaySettings


class DisplaySettings(QWidget):
    def __init__(self, parent, palette):
        super().__init__()
        self.parent = parent
        self.palette = palette
        self.global_config = get_config_file()
        self.dark_mode_enabled = get_config_file()["dark_mode"]
        self.interval = self.get_interval()
        self.ma_window_size = get_config_data("ma_window_size")

        self.curve_colors = self.get_curve_colors()
        self.flag_colors = self.get_flag_colors()

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        self.splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)

        # region - left widget
        self.left_widget = QWidget()
        self.left_widget.setFixedWidth(300)
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

        # region - palette label
        self.palette_widget = QWidget()
        self.palette_layout = QHBoxLayout()
        self.palette_widget.setLayout(self.palette_layout)
        self.left_layout.addWidget(self.palette_widget)
        self.palette_label = QLabel("Current Palette :")
        self.palette_label.setAlignment(Qt.AlignCenter)
        self.palette_layout.addWidget(self.palette_label)

        # region - palette combobox
        self.palette_combo = QComboBox(self)
        self.palette_combo.addItems(self.palette.get_palette_names())
        self.palette_combo.setCurrentText(self.palette.palette_name)
        self.palette_combo.currentTextChanged.connect(self.select_palette)
        self.palette_layout.addWidget(self.palette_combo)

        self.add_btn = QPushButton("+")
        self.add_btn.setFixedSize(20, 20)
        self.add_btn.clicked.connect(self.add_palette)
        self.palette_layout.addWidget(self.add_btn)

        self.rm_btn = QPushButton("-")
        self.rm_btn.setFixedSize(20, 20)
        self.rm_btn.clicked.connect(self.rm_palette)
        self.palette_layout.addWidget(self.rm_btn)

        # ------------------------------------------------------------------------------------------
        # region - Colors and styles

        # ----------------------------------------------------------- CURVES
        section_label = QLabel("Raw curves style")
        section_label.setAlignment(Qt.AlignCenter)
        self.left_layout.addWidget(section_label)

        self.curve_color_widget = ColorPickerWidget(
            palette=self.palette, type="curve", update_plot_ex=self.plot_example
        )
        self.left_layout.addWidget(self.curve_color_widget)

        self.curves_style_setter = StyleSetter(
            palette=self.palette, type="curve", update_plot_ex=self.plot_example
        )
        self.left_layout.addWidget(self.curves_style_setter)

        # ----------------------------------------------------------- MA CURVES
        self.ma_label = QLabel("Moving Average curves style")
        self.ma_label.setAlignment(Qt.AlignCenter)
        self.left_layout.addWidget(self.ma_label)

        self.ma_curves_style_setter = StyleSetter(
            palette=self.palette, type="ma_curve", update_plot_ex=self.plot_example
        )
        self.left_layout.addWidget(self.ma_curves_style_setter)

        # ------------------------------------------------------------------------------------------
        # region - MA WINDOW
        self.ma_window_widget = QWidget()
        self.ma_window_layout = QHBoxLayout()

        self.ma_window_label = QLabel("Moving Avg window size :")
        self.ma_window_input = QLineEdit()
        self.ma_window_layout.addWidget(self.ma_window_label)
        self.ma_window_layout.addWidget(self.ma_window_input)
        self.ma_window_widget.setLayout(self.ma_window_layout)

        self.ma_window_input.setPlaceholderText(f"{self.ma_window_size}")
        self.ma_window_input.editingFinished.connect(self.set_ma_window_size)
        self.left_layout.addWidget(self.ma_window_widget)

        # ----------------------------------------------------------- FLAGS
        section_label_2 = QLabel("Flags style")
        section_label_2.setAlignment(Qt.AlignCenter)
        self.left_layout.addWidget(section_label_2)

        self.flag_color_widget = ColorPickerWidget(
            palette=self.palette, type="flag", update_plot_ex=self.plot_example,
        )
        self.left_layout.addWidget(self.flag_color_widget)

        self.flags_style_setter = StyleSetter(
            palette=self.palette, type="flag", update_plot_ex=self.plot_example
        )
        self.left_layout.addWidget(self.flags_style_setter)

        # ------------------------------------------------------------------------------------------
        # region - upd interval
        self.interval_widget = QWidget()
        self.interval_layout = QHBoxLayout()

        self.interval_label = QLabel("Graph update interval (s) :")
        self.interval_input = QLineEdit()
        self.interval_layout.addWidget(self.interval_label)
        self.interval_layout.addWidget(self.interval_input)
        self.interval_widget.setLayout(self.interval_layout)

        self.interval_input.setPlaceholderText(f"{self.interval}")
        self.interval_input.editingFinished.connect(self.set_interval)
        self.left_layout.addWidget(self.interval_widget)

        self.plot_example()

        self.set_dark_mode(self.global_config["dark_mode"])

        self.show()

    # region - select_palette
    def select_palette(self, palette_name):
        """Select a palette by name and update the colors and styles."""
        self.palette.set_palette(palette_name)
        self.curve_color_widget.reset_buttons()
        self.flag_color_widget.reset_buttons()

        self.curves_style_setter.init_values()
        self.ma_curves_style_setter.init_values()
        self.flags_style_setter.init_values()

        self.plot_example()

    # region - plot_example
    def plot_example(self):
        curve_colors = self.get_curve_colors()
        flags_colors = self.get_flag_colors()

        curves_ls, curves_alpha = self.get_curves_style()
        ma_curves_ls, ma_curves_alpha = self.get_ma_curves_style()
        flags_ls, flags_alpha = self.get_flags_style()

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
        # numpy seed
        np.random.seed(42)
        amplitudes = np.random.uniform(0.5, 2.0, size=len(curve_colors))
        # amplitudes = [1, 2, 0.5, 1.5, 0.8]
        for i, (color, amp) in enumerate(zip(curve_colors, amplitudes)):
            y = amp * np.sin(x + i) + np.random.normal(0, 0.05, len(x))
            ax.plot(x, y, color=color, label=f"Curve {i + 1}", ls=curves_ls, alpha=curves_alpha)

            ax.plot(x, compute_moving_average(y, 10), color=color, label=f"MA Curve {i + 1}", ls=ma_curves_ls, alpha=ma_curves_alpha)

        coords = np.linspace(0, 2 * np.pi, len(flags_colors) + 2)
        for i, (color, x) in enumerate(zip(flags_colors, coords[1:-1])):
            y = amp * np.sin(x + i)
            ax.axvline(x, color=color, label=f"Flag {i + 1}", ls=flags_ls, alpha=flags_alpha)

        ax.legend(facecolor=bg_color, edgecolor=text_color, labelcolor=text_color)

        ax.set_title("Example Plot")
        ax.set_xlabel("X-axis")
        ax.set_ylabel("Y-axis")
        self.canvas.draw()

    def set_dark_mode(self, dark_mode):
        set_config_data('dark_mode', dark_mode)
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

            self.curve_color_widget.update_colors()
            self.flag_color_widget.update_colors()

            pixmap = QPixmap('xview/logo_dark.png')  # Replace with your logo path
            pixmap = pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)

            self.setPalette(dark_palette)
            self.dark_mode_enabled = True

            self.setWindowIcon(QIcon("logo_dark.png"))
            self.dark_mode_btn.setText("Light mode")
        else:
            self.setPalette(QApplication.style().standardPalette())
            self.curve_color_widget.update_colors()
            self.flag_color_widget.update_colors()
            self.dark_mode_enabled = False
            self.setWindowIcon(QIcon("logo_light.png"))
            self.dark_mode_btn.setText("Dark mode")

            pixmap = QPixmap('xview/logo_light.png')  # Replace with your logo path
            pixmap = pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)

        self.plot_example()

    def toggle_dark_mode(self):
        self.set_dark_mode(not self.dark_mode_enabled)
        self.parent.set_dark_mode(self.dark_mode_enabled)  # Notify parent if needed

    def get_curve_colors(self):
        if self.dark_mode_enabled:
            return self.palette.dark_mode_curves
        else:
            return self.palette.light_mode_curves

    def get_flag_colors(self):
        if self.dark_mode_enabled:
            return self.palette.dark_mode_flags
        else:
            return self.palette.light_mode_flags

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
        return self.palette.curves_ls, self.palette.curves_alpha

    def get_ma_curves_style(self):
        return self.palette.ma_curves_ls, self.palette.ma_curves_alpha

    def get_flags_style(self):
        return self.palette.flags_ls, self.palette.flags_alpha

    def get_interval(self):
        config = get_config_file()
        return config["update_interval"]

    def set_interval(self):
        interval = self.interval_input.text()
        self.interval = float(interval)
        set_config_data('update_interval', self.interval)

    def set_ma_window_size(self):
        ma_window_size = self.ma_window_input.text()
        self.ma_window_size = int(ma_window_size)
        set_config_data('ma_window_size', self.ma_window_size)

    def add_palette(self):
        new_palette_name, ok = QInputDialog.getText(self, "Add Palette", "Enter new palette name:")
        if ok and new_palette_name not in self.palette.get_palette_names():
            self.palette.add_palette(new_palette_name)
            self.palette_combo.addItem(new_palette_name)
            self.palette_combo.setCurrentText(new_palette_name)
            self.select_palette(new_palette_name)
        elif ok and new_palette_name in self.palette.get_palette_names():
            existing_palette_diag = QDialog()
            if get_config_data("dark_mode"):
                existing_palette_diag.setStyleSheet("background-color: #191919; color: white;")
            existing_palette_diag.setWindowTitle("Palette Exists")
            existing_palette_diag.setGeometry(100, 100, 300, 100)
            existing_palette_label = QLabel(f"Palette '{new_palette_name}' already exists.", existing_palette_diag)
            existing_palette_label.setAlignment(Qt.AlignCenter)
            existing_palette_diag.setLayout(QVBoxLayout())
            existing_palette_diag.layout().addWidget(existing_palette_label)
            existing_palette_diag.exec_()


    def rm_palette(self):
        self.palette_combo.blockSignals(True)  #  bloquer les signaux pour éviter les boucles infinies
        # enelevr la palette actuelle
        palette_list = self.palette.get_palette_names()
        self.palette.remove_palette()

        palette_list = self.palette.get_palette_names()
        if len(palette_list) == 0:  #  si il n'y a plus de palettes
            self.palette.add_palette("default")  #  ajouter une palette par défaut
            new_palette_name = "default"
        else:
            new_palette_name = palette_list[0]

        #  mettre à jour la combobox
        self.palette_combo.clear()
        self.palette_combo.addItems(self.palette.get_palette_names())

        self.palette_combo.setCurrentText(new_palette_name)
        self.palette_combo.blockSignals(False)
        self.select_palette(new_palette_name)

