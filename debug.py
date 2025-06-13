from xview.utils.utils import write_json
from xview import CONFIG_FILE_DIR
import os


palette_config_file = os.path.join(CONFIG_FILE_DIR, "palette_config.json")

palette_dict = {
    "custom": {
        "light_mode_curves": ["#ff8288", "#c28cff", "#99b1ff", "#8aff9c"],
        "dark_mode_curves": ["#F6EFBD", "#e4b074", "#BC7C7C", "#9090ff"],
        "light_mode_flags": ["#ff2410", "#000000"],
        "dark_mode_flags": ["#b2b4b0", "#fff6ee"],
        "curves_ls": "-",
        "curves_alpha": 1.0,
        "flags_ls": "-",
        "flags_alpha": 1.0,
        "ma_curves_ls": "--",
        "ma_curves_alpha": 0.5,
    },
    "default": {
        "light_mode_curves": ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"],
        "dark_mode_curves": ["#A2D2DF", "#F6EFBD", "#E4C087", "#BC7C7C", "#FF00FF"],
        "light_mode_flags": ["#000000", "#000000", "#000000"],
        "dark_mode_flags": ["#fafafa", "#fafafa", "#fafafa"],
        "curves_ls": "-",
        "curves_alpha": 1.0,
        "flags_ls": "-",
        "flags_alpha": 1.0,
        "ma_curves_ls": "--",
        "ma_curves_alpha": 0.5,
    }
}

write_json(palette_config_file, palette_dict)
