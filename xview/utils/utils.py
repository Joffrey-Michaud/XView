"""Generic JSON/file helpers and small numeric utilities used by XView."""

import json
import numpy as np


def write_json(json_path, my_dict):
    """Write a dict to a JSON file with indentation."""
    with open(json_path, "w") as f:
        json.dump(my_dict, f, indent=4)


def read_json(json_path):
    """Read a JSON file, retrying on transient decode errors."""
    while True:
        try:
            with open(json_path, "r") as f:
                my_dict = json.load(f)
            return my_dict
        except json.JSONDecodeError:
            pass


def write_file(path_to_file, word, flag="w"):
    """Append or overwrite a line to a text file, coercing non-strings."""
    if not isinstance(word, str):
        word = str(word)
    with open(path_to_file, flag) as f:
        f.write(word + "\n")


def read_file(file_to_path, return_str=False):
    """Read a text file; return first line (str) or all as float array.

    Args:
        file_to_path: Path to the text file.
        return_str: If True, return the first non-empty line as a string.
                    Otherwise, return an array of floats parsed from lines.
    """
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
    """Compute a simple moving average over a list/array."""
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
