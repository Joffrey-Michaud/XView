"""Palette configuration management for display colors and styles.

The palette configuration file is a JSON map of palette names to settings
such as light/dark colors for curves and flags, line styles, and alpha.
Example structure:

{
    "custom": {
        "light_mode_curves": ["#FF0000", "#00FF00", "#0000FF"],
        "dark_mode_curves": ["#A2D2DF", "#F6EFBD", "#E4C087"],
        "light_mode_flags": ["#000000", "#000000", "#000000"],
        "dark_mode_flags": ["#fafafa", "#fafafa", "#fafafa"],
        "curves_ls": "-",
        "curves_alpha": 1.0,
        "flags_ls": "-",
        "flags_alpha": 1.0,
        "ma_curves_ls": "--",
        "ma_curves_alpha": 0.5
    }
}
"""

from xview import CONFIG_FILE_DIR
import json
import os
from xview import set_config_data

DEFAULT_PALETTE = {
    "light_mode_curves": ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"],
    "dark_mode_curves": ["#A2D2DF", "#F6EFBD", "#E4C087", "#BC7C7C", "#FF00FF"],
    "light_mode_flags": ["#000000", "#000000", "#000000"],
    "dark_mode_flags": ["#fafafa", "#fafafa", "#fafafa"],
    "curves_ls": "-",
    "curves_alpha": 1.0,
    "flags_ls": "-",
    "flags_alpha": 1.0,
    "ma_curves_ls": "--",
    "ma_curves_alpha": 0.5
}


class Palette(object):
    """Load/update/save named color/style palettes used for plotting."""

    def __init__(self, palette_name="default"):
        self.config_file = os.path.join(CONFIG_FILE_DIR, "palette_config.json")
        self.palette_name = palette_name

        self.light_mode_curves = None
        self.dark_mode_curves = None
        self.light_mode_flags = None
        self.dark_mode_flags = None
        self.curves_ls = None
        self.curves_alpha = None
        self.flags_ls = None
        self.flags_alpha = None
        self.ma_curves_ls = None
        self.ma_curves_alpha = None

        self.set_palette(self.palette_name)

    #  lire le fichier de configuration des palettes
    def get_config_file(self):
        """Read and return the palette JSON config as a dictionary."""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"No palette config file found at {self.config_file}.")
        config = json.load(open(self.config_file))
        return config

    #  lire une seule palette
    def get_config_palette(self, palette_name):
        """Return a single palette dict by name; raise if not found."""
        palette = self.get_config_file().get(palette_name, None)
        if palette is None:
            raise ValueError(f"Palette '{palette_name}' not found in the config file.")
        return palette

    #  réécrire le fichier de configuration des palettes
    def set_config_file(self, config):
        """Overwrite the palette config file with the provided mapping."""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)

    # écrire une palette dans le fichier de configuration
    def set_config_palette(self):
        """Persist the current in-memory palette values under its name."""
        config = self.get_config_file()

        palette_config = {
            "light_mode_curves": self.light_mode_curves,
            "dark_mode_curves": self.dark_mode_curves,
            "light_mode_flags": self.light_mode_flags,
            "dark_mode_flags": self.dark_mode_flags,
            "curves_ls": self.curves_ls,
            "curves_alpha": self.curves_alpha,
            "flags_ls": self.flags_ls,
            "flags_alpha": self.flags_alpha,
            "ma_curves_ls": self.ma_curves_ls,
            "ma_curves_alpha": self.ma_curves_alpha
        }

        config[self.palette_name] = palette_config
        self.set_config_file(config)

    def set_palette(self, palette_name):
        """Load a palette by name into the object's attributes and select it."""
        palette = self.get_config_palette(palette_name)
        self.light_mode_curves = palette.get("light_mode_curves", [])
        self.dark_mode_curves = palette.get("dark_mode_curves", [])
        self.light_mode_flags = palette.get("light_mode_flags", [])
        self.dark_mode_flags = palette.get("dark_mode_flags", [])
        self.curves_ls = palette.get("curves_ls", "-")
        self.curves_alpha = palette.get("curves_alpha", 1.0)
        self.flags_ls = palette.get("flags_ls", "-")
        self.flags_alpha = palette.get("flags_alpha", 1.0)
        self.ma_curves_ls = palette.get("ma_curves_ls", "--")
        self.ma_curves_alpha = palette.get("ma_curves_alpha", 0.5)

        self.palette_name = palette_name
        set_config_data('palette_name', palette_name)

    def add_curve_color(self, color_name):
        """Append a new color to both light and dark curve lists and save."""
        self.light_mode_curves.append(color_name)
        self.dark_mode_curves.append(color_name)
        self.set_config_palette()

    def add_flag_color(self, color_name):
        """Append a new color to both light and dark flag lists and save."""
        self.light_mode_flags.append(color_name)
        self.dark_mode_flags.append(color_name)
        self.set_config_palette()

    def rm_curve_color(self, idx):
        """Remove a curve color by index from light/dark lists and save."""
        if idx < len(self.light_mode_curves):
            self.light_mode_curves.pop(idx)
        if idx < len(self.dark_mode_curves):
            self.dark_mode_curves.pop(idx)
        self.set_config_palette()

    def rm_flag_color(self, idx):
        """Remove a flag color by index from light/dark lists and save."""
        if idx < len(self.light_mode_flags):
            self.light_mode_flags.pop(idx)
        if idx < len(self.dark_mode_flags):
            self.dark_mode_flags.pop(idx)
        self.set_config_palette()

    def get_palette_names(self):
        """Return the list of available palette names."""
        return list(self.get_config_file().keys())

    def add_palette(self, palette_name):
        """Create a new palette from defaults and select it."""
        config = self.get_config_file()
        config[palette_name] = DEFAULT_PALETTE
        self.set_config_file(config)
        self.set_palette(palette_name)

    def remove_palette(self):
        """Delete the current palette if it exists in the config file."""
        config = self.get_config_file()
        if self.palette_name in config:
            del config[self.palette_name]
            self.set_config_file(config)
