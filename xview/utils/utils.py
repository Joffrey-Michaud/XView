import json
import numpy as np


def write_json(json_path, my_dict):
    with open(json_path, "w") as f:
        json.dump(my_dict, f)


def read_json(json_path):
    with open(json_path, "r") as f:
        my_dict = json.load(f)
    return my_dict


def write_file(path_to_file, word, flag="w"):
    if not isinstance(word, str):
        word = str(word)
    with open(path_to_file, flag) as f:
        f.write(word + "\n")


def read_file(file_to_path, return_str=False):
    with open(file_to_path, "r") as f:
        data = f.read()
    splitted = data.split("\n")
    splitted.pop()
    if return_str:
        return str(splitted[0])
    return np.asarray(splitted, dtype=np.float32)


def compute_moving_average(values, window_size=15):
    means = []
    for i in range(len(values)):
        low = max(0, i - window_size + 1)
        current_window = values[low: i + 1]
        means.append(np.mean(current_window))
    return means


def is_dark_mode_enabled(config_file):
    dark_mode_enabled = read_json(config_file)["dark_mode"]
    return dark_mode_enabled