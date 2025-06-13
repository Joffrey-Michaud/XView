import os
import json

# /home/<username>/.xview/config.json
CONFIG_FILE_DIR = os.path.dirname(f"{os.path.expanduser('~')}/.xview/")
os.makedirs(CONFIG_FILE_DIR, exist_ok=True)
CONFIG_FILE_PATH = f"{CONFIG_FILE_DIR}/config.json"

default_config = {
    "data_folder": None,
    "dark_mode_curves": ["#A2D2DF", "#F6EFBD", "#E4C087", "#BC7C7C", "#FF00FF"],
    "dark_mode_flags": ["#fafafa", "#fafafa", "#fafafa"],
    "light_mode_curves": ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"],
    "light_mode_flags": ["#000000", "#000000", "#000000"],
    "curves_ls": "-",
    "curves_alpha": 1.0,
    "flags_ls": "-",
    "flags_alpha": 1.0,
    "ma_curves_ls": "--",
    "ma_curves_alpha": 0.5,
    "palette_name": "default",
    "ma_window_size": 15,
    "update_interval": 60,
    "dark_mode": False,
    "remind_me_later_date": None,
    "first_since_update": False,
    "auto_update": False,
    "version": "1.0.2"
}

default_palette_config = {
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
        "ma_curves_alpha": 0.5
    },
    "cyberpunk": {
        "light_mode_curves": ["#FF00FF", "#00FFFF", "#FF6EC7", "#39FF14", "#FFD700"],
        "dark_mode_curves": ["#FF00FF", "#00FFF7", "#8A2BE2", "#39FF14", "#FF6EC7"],
        "light_mode_flags": ["#0F0F0F", "#0F0F0F", "#0F0F0F"],
        "dark_mode_flags": ["#f0f0f0", "#FF00FF", "#00FFFF"],
        "curves_ls": "-",
        "curves_alpha": 0.9,
        "flags_ls": ":",
        "flags_alpha": 0.8,
        "ma_curves_ls": "--",
        "ma_curves_alpha": 0.4
    },
    "desert": {
        "light_mode_curves": ["#D2B48C", "#CD853F", "#DEB887", "#F4A460", "#E9967A"],
        "dark_mode_curves": ["#A0522D", "#C68642", "#B87333", "#DAA520", "#8B4513"],
        "light_mode_flags": ["#4B3621", "#6B4423", "#5C4033"],
        "dark_mode_flags": ["#FFDAB9", "#FFE4B5", "#FAEBD7"],
        "curves_ls": "-",
        "curves_alpha": 0.95,
        "flags_ls": "--",
        "flags_alpha": 0.8,
        "ma_curves_ls": "--",
        "ma_curves_alpha": 0.5
    },
    "deep ocean": {
        "light_mode_curves": ["#0077BE", "#00A1D9", "#009688", "#4DD0E1", "#00BFA6"],
        "dark_mode_curves": ["#0F2B46", "#145374", "#0C7B93", "#119DA4", "#88D498"],
        "light_mode_flags": ["#003B46", "#002F2F", "#003E3E"],
        "dark_mode_flags": ["#B2EBF2", "#A7FFEB", "#80DEEA"],
        "curves_ls": "-",
        "curves_alpha": 0.9,
        "flags_ls": "--",
        "flags_alpha": 0.7,
        "ma_curves_ls": ":",
        "ma_curves_alpha": 0.5
    },
    "forest": {
        "light_mode_curves": ["#2E8B57", "#556B2F", "#6B8E23", "#8FBC8F", "#BA55D3"],
        "dark_mode_curves": ["#013220", "#3B5323", "#4B0082", "#7D5BA6", "#ADFF2F"],
        "light_mode_flags": ["#3C2F2F", "#4F3A3A", "#2F4F2F"],
        "dark_mode_flags": ["#E6E6FA", "#D8BFD8", "#98FB98"],
        "curves_ls": "-",
        "curves_alpha": 0.85,
        "flags_ls": "-.",
        "flags_alpha": 0.75,
        "ma_curves_ls": ":",
        "ma_curves_alpha": 0.4
    }

}


def config_exists():
    return os.path.exists(CONFIG_FILE_PATH)


def get_config_file():
    if not os.path.exists(CONFIG_FILE_PATH):
        raise FileNotFoundError(f"No config file found, launch config.py before running any xview functions.")
    config = json.load(open(CONFIG_FILE_PATH))
    return config


def get_config_data(key):
    return get_config_file().get(key, None)


def set_config_file(config):
    with open(CONFIG_FILE_PATH, 'w') as f:
        json.dump(config, f, indent=4)


def set_config_data(key, value):
    config = get_config_file()
    config[key] = value
    set_config_file(config)


def check_config_integrity():
    """
    Check if the config file has all required keys.
    If not, it will create a new config file with default values.
    """
    # required_keys = ["data_folder", "dark_mode_curves", "dark_mode_flags", "light_mode_curves", "light_mode_flags", "curves_ls", "curves_alpha", "flags_ls", "flags_alpha", "ma_curves_ls", "ma_curves_alpha", "update_interval", "dark_mode", "remind_me_later_date", "first_since_update", "auto_update"]
    required_keys = default_config.keys()  # Use the keys from the default config
    config = get_config_file()

    for key in required_keys:
        if key not in config:
            config[key] = default_config[key]  # Set default value or handle as needed
            if key == "data_folder":
                config[key] = os.path.dirname(f"{os.path.expanduser('~')}/.xview/exps/")

    set_config_file(config)
    set_config_data("version", default_config["version"])  # Ensure version is set to the default version

    if not os.path.exists(os.path.join(CONFIG_FILE_DIR, "palette_config.json")):
        with open(os.path.join(CONFIG_FILE_DIR, "palette_config.json"), 'w') as f:
            json.dump(default_palette_config, f, indent=4)
