import sys
from PyQt5.QtWidgets import QApplication, QFileDialog, QWidget, QPushButton, QVBoxLayout, QSplitter, QGridLayout, QMainWindow, QHBoxLayout, QColorDialog
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap, QIcon, QPalette, QColor
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from xview.utils.utils import write_json, read_json
import os
import numpy as np


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



class FolderSelector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("XView - Config")
        self.setWindowIcon(QIcon("logo_light.png"))
        self.setGeometry(300, 300, 1500, 750)

        self.dark_mode_curves = self.get_color_theme("curves", dark_mode=True)
        self.dark_mode_flags = self.get_color_theme("flags", dark_mode=True)

        self.light_mode_curves = self.get_color_theme("curves", dark_mode=False)
        self.light_mode_flags = self.get_color_theme("flags", dark_mode=False)

        self.current_exp_folder = self.get_current_exps_folder()

        self.dark_mode_enabled = False

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

        self.exp_folder_label = QLabel(f"Current exps folder :\n{self.current_exp_folder}")
        self.exp_folder_label.setWordWrap(True)
        self.exp_folder_label.setStyleSheet("font-size: 15px;")
        self.exp_folder_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.exp_folder_label, 1, 0)
        
        exp_btn = QPushButton('Choose Exps Folder', self)
        exp_btn.clicked.connect(self.change_exp_folder)
        left_layout.addWidget(exp_btn, 2, 0)

        self.dark_mode_btn = QPushButton('Dark Mode', self)
        self.dark_mode_btn.clicked.connect(self.toggle_dark_mode)
        left_layout.addWidget(self.dark_mode_btn, 3, 0)
        # self.setLayout(layout)

        section_label = QLabel("Choose the colors of the curves")
        section_label.setStyleSheet("font-size: 15px;")
        section_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(section_label, 4, 0)

        self.color_widget = ColorPickerWidget(colors=self.light_mode_curves, on_color_change=self.update_curves_colors)
        left_layout.addWidget( self.color_widget, 5, 0)

        section_label_2 = QLabel("Choose the colors of the flags")
        section_label_2.setStyleSheet("font-size: 15px;")
        section_label_2.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(section_label_2, 6, 0)

        self.color_widget_2 = ColorPickerWidget(colors=self.light_mode_flags, on_color_change=self.update_flags_colors)
        left_layout.addWidget( self.color_widget_2, 7, 0)

        # save button
        save_btn = QPushButton('Save')
        save_btn.clicked.connect(self.save_config)
        left_layout.addWidget(save_btn, 8, 0)

        # figure widget
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        splitter.addWidget(self.canvas)

        self.plot_example()

        self.show()

    def change_exp_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder_path:
            self.current_exp_folder = folder_path
            self.exp_folder_label.setText(f"Current exps folder :\n{self.current_exp_folder}")

        # if folder_path:
        #     config = {"data_folder": folder_path}
        #     os.makedirs(os.path.join("xview", "config"), exist_ok=True)
        #     write_json(os.path.join("xview", "config", "config.json"), config)

        # self.close()

    def save_config(self):
        config = {
            "data_folder": self.current_exp_folder,
            "dark_mode_curves": self.dark_mode_curves,
            "dark_mode_flags": self.dark_mode_flags,
            "light_mode_curves": self.light_mode_curves,
            "light_mode_flags": self.light_mode_flags
        }
        os.makedirs(os.path.join("xview", "config"), exist_ok=True)
        write_json(os.path.join("xview", "config", "config.json"), config)
        print("Configuration saved to config.json")
        self.close()

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

        x = np.linspace(0, 2 * np.pi, 200)
        amplitudes = [1, 2, 0.5, 1.5, 0.8]
        for i, (color, amp) in enumerate(zip(curves_colors, amplitudes)):
            y = amp * np.sin(x + i)
            ax.plot(x, y, color=color, label=f"Curve {i+1}")

        coords = np.linspace(0, 2 * np.pi, 5)
        for i, (color, x)  in enumerate(zip(flags_colors, coords[1:-1])):
            y = amp * np.sin(x + i)
            ax.axvline(x, color=color, label=f"Flag {i+1}")


        # x = np.linspace(0, 2 * np.pi, 200)
        # for i, color in enumerate(curves_colors):
        #     y = np.sin(x + i)
        #     ax.plot(x, y, color=color, label=f"Sin {i+1}")

        ax.legend(facecolor=bg_color, edgecolor=text_color, labelcolor=text_color)

        ax.set_title("Example Plot")
        ax.set_xlabel("X-axis")
        ax.set_ylabel("Y-axis")
        self.canvas.draw()


    def toggle_dark_mode(self):
        print("DARK MODE STATE :", self.dark_mode_enabled)
        if not self.dark_mode_enabled:
            self.dark_mode_enabled = True
            self.set_dark_mode()
            self.setWindowIcon(QIcon("logo_dark.png"))
            # dark_mode_btn = self.sender()
            self.dark_mode_btn.setText("Light mode")
        else:
            self.dark_mode_enabled = False
            self.set_light_mode()
            self.setWindowIcon(QIcon("logo_light.png"))
            self.dark_mode_btn.setText("Dark mode")
        self.plot_example()
        # self.display_model_image()

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

        self.color_widget.update_colors(self.dark_mode_curves)
        self.color_widget_2.update_colors(self.dark_mode_flags)

        
#         self.setStyleSheet("""
#     QPushButton {
#         background-color: #353535;
#         color: white;
#         border: 1px solid #5c5c5c;
#         padding: 5px;
#     }
#     QPushButton:hover {
#         background-color: #444444;
#     }
# """)

        self.setPalette(dark_palette)

    def set_light_mode(self):
        self.setPalette(QApplication.style().standardPalette())
        self.color_widget.update_colors(self.light_mode_curves)
        self.color_widget_2.update_colors(self.light_mode_flags)
        # self.setStyleSheet("")

    def get_color_theme(self, color_section="curves", dark_mode=False):
        if color_section == "curves":
            if dark_mode:
                if os.path.isfile(os.path.join("xview", "config", "config.json")):
                    print("dark mode, curves")
                    # Read the JSON file
                    return read_json(os.path.join("xview", "config", "config.json"))[f"dark_mode_curves"]
                else:
                    print("dark mode, curves, default")
                    return ["#A2D2DF", "#F6EFBD", "#E4C087", "#BC7C7C", "#FF00FF"]
            else:
                if os.path.isfile(os.path.join("xview", "config", "config.json")):
                    # Read the JSON file
                    print("light mode, curves")
                    colors = read_json(os.path.join("xview", "config", "config.json"))[f"light_mode_curves"]
                    return read_json(os.path.join("xview", "config", "config.json"))[f"light_mode_curves"]
                else:
                    print("light mode, curves, default")
                    return ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"]
        
        elif color_section == "flags":
            if dark_mode:
                if os.path.isfile(os.path.join("xview", "config", "config.json")):
                    # Read the JSON file
                    return read_json(os.path.join("xview", "config", "config.json"))[f"dark_mode_flags"]
                else:
                    return ["#fafafa", "#fafafa", "#fafafa"]
            else:
                if os.path.isfile(os.path.join("xview", "config", "config.json")):
                    # Read the JSON file
                    return read_json(os.path.join("xview", "config", "config.json"))[f"light_mode_flags"]
                else:
                    return ["#000000", "#000000", "#000000"]
                
    def get_current_exps_folder(self):
        if os.path.isfile(os.path.join("xview", "config", "config.json")):
            # Read the JSON file
            return read_json(os.path.join("xview", "config", "config.json"))["data_folder"]
        else:
            return "No folder selected"
                
    def update_curves_colors(self, index, new_color):
        if self.dark_mode_enabled:
            self.dark_mode_curves[index] = new_color
        else:
            self.light_mode_curves[index] = new_color

        self.plot_example()

    def update_flags_colors(self, index, new_color):
        if self.dark_mode_enabled:
            self.dark_mode_flags[index] = new_color
        else:
            self.light_mode_flags[index] = new_color

        self.plot_example()

    




if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    ex = FolderSelector()
    sys.exit(app.exec_())