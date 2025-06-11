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
    "ma_window_size": 15,
    "update_interval": 60,
    "dark_mode": False,
    "remind_me_later_date": None,
    "first_since_update": False,
    "auto_update": False,
    "version": "1.0.2"
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
