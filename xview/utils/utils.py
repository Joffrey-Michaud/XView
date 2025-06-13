import json
import numpy as np


def write_json(json_path, my_dict):
    with open(json_path, "w") as f:
        json.dump(my_dict, f, indent=4)


def read_json(json_path):
    while True:
        try:
            with open(json_path, "r") as f:
                my_dict = json.load(f)
            return my_dict
        except json.JSONDecodeError:
            pass


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
        if len(splitted) == 0:
            return ""
        return str(splitted[0])
    return np.asarray(splitted, dtype=np.float32)


def compute_moving_average(values, window_size=15):
    means = []
    for i in range(len(values)):
        low = max(0, i - window_size + 1)
        current_window = values[low: i + 1]
        means.append(np.mean(current_window))
    return means


# def compute_moving_average(values, window_size=15, alpha=0.1):
#     # window size est là juste pour éviter un bug pour tester
#     smoothed = [values[0]]
#     for v in values[1:]:
#         smoothed.append(alpha * v + (1 - alpha) * smoothed[-1])
#     return smoothed
