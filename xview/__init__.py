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
    "trash_dir": None,
    "trash_max_size": 3,  # in Gb. 0 means no limit
    "trash_max_days": 30,  # in days. 0 means no limit
    "version": "1.0.12"
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
        "light_mode_curves": ["#E0C097", "#C68642", "#F4A261", "#A0522D", "#FFE8A3"],
        "dark_mode_curves": ["#D9BF77", "#CC7722", "#A65E2E", "#803D3B", "#D89216"],
        "light_mode_flags": ["#9B6A6C", "#5E3023", "#FF9B54"],
        "dark_mode_flags": ["#FFFAE5", "#FFD166", "#EF476F"],
        "curves_ls": "-",
        "curves_alpha": 0.95,
        "flags_ls": "--",
        "flags_alpha": 0.8,
        "ma_curves_ls": "--",
        "ma_curves_alpha": 0.5
    },
    "deep ocean": {
        "light_mode_curves": ["#0A369D", "#4472CA", "#1C7293", "#70C1B3", "#9EE493"],
        "dark_mode_curves": ["#20639B", "#3CAEA3", "#F6D55C", "#173F5F", "#ED553B"],
        "light_mode_flags": ["#3E517A", "#FF6B6B", "#4ECDC4"],
        "dark_mode_flags": ["#F25F5C", "#FFE066", "#F3FFBD"],
        "curves_ls": "-",
        "curves_alpha": 0.9,
        "flags_ls": "--",
        "flags_alpha": 0.7,
        "ma_curves_ls": ":",
        "ma_curves_alpha": 0.5
    },
    "forest": {
        "light_mode_curves": ["#1B4332", "#2F5233", "#6A994E", "#A0522D", "#3E1F47"],
        "dark_mode_curves": ["#A8E6A1", "#C0FDFB", "#F6D186", "#FFB5A7", "#E8EDDF"],
        "light_mode_flags": ["#9E2A2B", "#4A4E69", "#1D3557"],
        "dark_mode_flags": ["#FFCF56", "#D4A5A5", "#C1FFD7"],
        "curves_ls": "-",
        "curves_alpha": 1.0,
        "flags_ls": "--",
        "flags_alpha": 0.9,
        "ma_curves_ls": ":",
        "ma_curves_alpha": 0.5
    },
    "pastel": {
        "light_mode_curves": ["#96d46f", "#e4b074", "#BC7C7C", "#cc99ff", "#FFBABA"],
        "dark_mode_curves": ["#b4ff86", "#e4b074", "#BC7C7C", "#cc99ff", "#FFBABA"],
        "light_mode_flags": ["#b48b8c", "#8c98b4", "#96b49d"],
        "dark_mode_flags": ["#b48b8c", "#8c98b4", "#96b49d"],
        "curves_ls": "-",
        "curves_alpha": 0.9,
        "flags_ls": "--",
        "flags_alpha": 0.7,
        "ma_curves_ls": ":",
        "ma_curves_alpha": 0.5
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
