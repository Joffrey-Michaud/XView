import os
import json

# /home/<username>/.xview/config.json
CONFIG_FILE_DIR = os.path.dirname(f"{os.path.expanduser('~')}/.xview/")
os.makedirs(CONFIG_FILE_DIR, exist_ok=True)
CONFIG_FILE_PATH = f"{CONFIG_FILE_DIR}/config.json"


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
