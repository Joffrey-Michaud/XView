"""Utilities for managing remote execution configurations.

This module provides simple helpers to create and delete remote configuration
entries stored in a JSON file named ``remote_config.json`` under
``xview.CONFIG_FILE_DIR``. Each entry is keyed by a user-defined remote name
and stores the host name, login, and experiment folder used by XView's remote
features.

File layout example::

    remote_config.json
    {
        "my_remote": {
            "host_name": "gpu.example.com",
            "login": "alice",
            "exp_folder": "/data/experiments"
        }
    }

Note:
    These helpers read and write the entire JSON file. They do not perform
    any validation beyond basic dictionary manipulation and will overwrite
    existing entries of the same ``remote_name``.
"""

from xview import CONFIG_FILE_DIR
import json
from pathlib import Path


def create_remote_config(remote_name, host_name, login, exp_folder):
    """Create or update a remote configuration entry.

    This function adds (or overwrites) a configuration entry identified by
    ``remote_name`` in ``remote_config.json``. If the configuration file does
    not exist yet, it will be created. Existing configurations are preserved
    unless they share the same ``remote_name``.

    Args:
        remote_name: Unique key for the remote configuration (e.g., "cluster-a").
        host_name: Hostname or IP of the remote machine.
        login: Username to use for the remote machine.
        exp_folder: Path on the remote machine where experiments are stored.

    Side Effects:
        Writes the JSON file at ``CONFIG_FILE_DIR/remote_config.json`` with the
        updated dictionary of configurations.

    Raises:
        json.JSONDecodeError: If the existing JSON file is malformed.
        OSError: If the configuration file cannot be read or written.
    """
    config_dict = {
        "host_name": host_name,
        "login": login,
        "exp_folder": exp_folder
    }

    remote_config_file = Path(CONFIG_FILE_DIR) / f"remote_config.json"
    if remote_config_file.exists():
        with open(remote_config_file, 'r') as f:
            existing_configs = json.load(f)
    else:
        existing_configs = {}

    existing_configs[remote_name] = config_dict

    with open(remote_config_file, 'w') as f:
        json.dump(existing_configs, f, indent=4)


def del_remote_config(remote_name):
    """Delete a remote configuration entry if it exists.

    Removes the entry keyed by ``remote_name`` from ``remote_config.json``.
    If the file or the entry doesn't exist, the function is a no-op other
    than rewriting the file (it will be created with an empty object if it
    was missing).

    Args:
        remote_name: The key of the configuration to remove.

    Side Effects:
        Writes the JSON file at ``CONFIG_FILE_DIR/remote_config.json`` with the
        updated dictionary of configurations.

    Raises:
        json.JSONDecodeError: If the existing JSON file is malformed.
        OSError: If the configuration file cannot be read or written.
    """
    remote_config_file = Path(CONFIG_FILE_DIR) / f"remote_config.json"
    if remote_config_file.exists():
        with open(remote_config_file, 'r') as f:
            existing_configs = json.load(f)
    else:
        existing_configs = {}

    if remote_name in existing_configs:
        del existing_configs[remote_name]

    with open(remote_config_file, 'w') as f:
        json.dump(existing_configs, f, indent=4)


def get_remote_configs():  # retrieve names of remotes
    """Retrieve the list of remote configuration names.

    Reads the ``remote_config.json`` file and returns a list of all keys
    (remote names) present in the file. If the file does not exist, an
    empty list is returned.

    Returns:
        A list of strings representing the remote configuration names.
    """
    remote_config_file = Path(CONFIG_FILE_DIR) / f"remote_config.json"
    if remote_config_file.exists():
        with open(remote_config_file, 'r') as f:
            existing_configs = json.load(f)
    else:
        existing_configs = {}

    return sorted(list(existing_configs.keys()))
