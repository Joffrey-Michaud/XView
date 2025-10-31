import os
import json
import sys
from pathlib import Path


from xview import CONFIG_FILE_PATH

print("Write the path to the directory where your experiments will be stored:")
data_folder = input("Experiments folder path: ").strip()

if not os.path.exists(data_folder):
    if input(f"The directory '{data_folder}' does not exist. Do you want to create it? (y/n)") == "y":
        os.makedirs(data_folder)
        print(f"Created directory: {data_folder}")
    else:
        print("Installation aborted. Please create the experiments directory and run the installer again.")
        sys.exit(1)

minimal_config_dict = {
    "data_folder": data_folder
    }
with open(CONFIG_FILE_PATH, 'w') as f:
    json.dump(minimal_config_dict, f, indent=4)