"""Experiment abstraction to create, track, and log metrics/flags on disk."""

import os
from xview.utils.utils import *
from xview.score import MultiScores
import shutil
from xview.version.update_project import warn_if_outdated
from xview import get_config_data


@warn_if_outdated
class Experiment(object):
    """Create and manage an on-disk experiment with scores and flags.

    Folder layout under data_folder/group/name includes JSON infos, status,
    per-metric score files, and flag files. Provides helpers to append points
    and keep a small JSON config for per-experiment settings.
    """

    def __init__(self, name, infos=None, group=None, clear=None, check_exists=False):
        """Object to manage an experiment folder.
        This class creates a folder for the experiment, manages its status, scores, and flags.
        It also allows to store and retrieve information about the experiment in a JSON file.
        The folder structure is as follows:
        data_folder/
            └── group_name/
                └── experiment_name/
                    ├── exp_infos.json
                    ├── status.txt
                    ├── scores_training.txt
                    ├── scores_validation.txt
                    ├── scores/
                    │   └── score_name.txt
                    └── flags/
                        └── flag_name.txt
        The `name` parameter is the name of the experiment, which will be used to create the folder and files.
        The `infos` parameter allows to set initial information for the experiment, which will be stored in a JSON file.
        The 'group' parameter allows to create a subfolder for the experiment, useful for organizing multiple experiments under a common group name.
        The `clear` parameter allows to delete the experiment folder if it already exists.
        The `check_exists` parameter raises an error if the experiment folder does not exist when set to True. It also ignore the `clear` parameter.

        The 'data_folder' is read from the configuration file, and defaults to '~/.xview/exps/' if not set. You can change this in the configuration file, or by running the `config.py` script.
        Args:
            name (string): Name of the experiment, used to create the folder and files.
            infos (dict, optional): Dict containing informations about the experiement. Defaults to None.
            group (string, optional): Name of the group in which to put the experiment. Defaults to None.
            clear (bool, optional): Set to True if you want to erase the experiment before running. Defaults to None.
            check_exists (bool, optional): Set to True if you want to assert the existence of the experiment in security, ignoring the clear parameter. Useful for inference for example. Defaults to False.

        Raises:
            FileNotFoundError: _description_
        """
        self.name = name
        self.group = group
        self.check_exists = check_exists
        self.pipes = list()

        # lecture du fichier de config et création du dossier de l'expérience
        self.data_folder = get_config_data("data_folder")

        if self.group is not None:
            self.data_folder = os.path.join(self.data_folder, self.group)

        self.experiment_folder = os.path.join(self.data_folder, self.name)

        if self.check_exists:
            clear = False
            exists = os.path.exists(self.experiment_folder)
            if not exists:
                raise FileNotFoundError(f"Experiment folder {self.experiment_folder} does not exist.")

        if clear == True and os.path.exists(self.experiment_folder):
            shutil.rmtree(self.experiment_folder)

        os.makedirs(self.experiment_folder, exist_ok=True)

        # créer le fichier d'infos si donnés
        self.infos_path = os.path.join(self.experiment_folder, "exp_infos.json")
        self.infos = self.get_infos()
        if infos is not None:
            self.set_infos(infos)

        # créer le fichier de status
        self.status = "init"
        self.status_file = os.path.join(self.experiment_folder, "status.txt")
        write_file(self.status_file, self.status, flag="w")

        # fichier de score training
        self.score_file_training = os.path.join(self.experiment_folder, "scores_training.txt")
        # fichier de score validation
        self.score_file_validation = os.path.join(self.experiment_folder, "scores_validation.txt")

        #  dossier de scores
        self.scores_folder = os.path.join(self.experiment_folder, "scores")
        os.makedirs(self.scores_folder, exist_ok=True)
        self.scores = MultiScores(self.scores_folder)

        #  dossier de flags
        self.flags_folder = os.path.join(self.experiment_folder, "flags")
        os.makedirs(self.flags_folder, exist_ok=True)
        self.flags = MultiScores(self.flags_folder)

        self.scores_monitoring = {}

    def pipe_to(self, other_experiment):
        """Forward write operations to another Experiment instance."""
        if hasattr(other_experiment, "__class__") and other_experiment.__class__.__name__ == "Experiment":
            self.pipes.append(other_experiment)
        else:
            raise TypeError("other_experiment must be an instance of Experiment")

    def pipe_break(self, other_experiment):
        """Stop forwarding to the provided Experiment instance."""
        if other_experiment in self.pipes:
            self.pipes.remove(other_experiment)
        else:
            raise ValueError("other_experiment is not in the list of pipes")

    def __act_pipe(self, method, *args, **kwargs):
        for pipe in self.pipes:
            getattr(pipe, method)(*args, **kwargs)

    def get_infos(self):
        """Return experiment metadata dict, creating an empty file if missing."""
        if os.path.exists(self.infos_path):
            self.infos = read_json(self.infos_path)
        else:
            self.infos = {}
            self.set_infos({})
        return self.infos

    def set_infos(self, infos):
        """Overwrite experiment metadata JSON with the provided dict."""
        self.__act_pipe("set_infos", infos)
        self.infos = infos
        if infos is not None:
            write_json(self.infos_path, infos)

    def set_info(self, key, value):
        """Set a single metadata key and persist to JSON."""
        self.__act_pipe("set_info", key, value)
        self.infos[key] = value
        write_json(self.infos_path, self.infos)

    def set_train_status(self):
        """Mark experiment status as 'training'."""
        self.update_status("training")

    def set_finished_status(self):
        """Mark experiment status as 'finished'."""
        self.update_status("finished")

    def update_status(self, status):
        """Write the status string to the status file and propagate to pipes."""
        self.__act_pipe("update_status", status)
        self.status = status
        write_file(self.status_file, self.status, flag="w")

    def add_score(self, name, y, x=None, plt_args: dict = None, label_value=None, monitor="max,min"):
        """Append a score point and ensure its Score exists with optional args."""
        self.__act_pipe("add_score", name, y, x, plt_args=plt_args, label_value=label_value, monitor=monitor)
        if name not in self.scores.scores:
            self.scores.add_score(name, plt_args=plt_args)
        self.scores.add_score_point(name, y, x, label_value=label_value)
        self.scores_monitoring[name] = monitor
        self.set_exp_config_data("scores_monitoring", self.scores_monitoring)

    def add_flag(self, name, x=None, unique=False, plt_args: dict = None, label_value=None):
        """Append a flag event (vertical line) to the flags collection."""
        self.__act_pipe("add_flag", name, x, unique=unique, plt_args=plt_args, label_value=label_value)
        if name not in self.flags.scores:
            self.flags.add_score(name, plt_args=plt_args)
        if x is None:
            x = max(len(self.scores), len(self.flags))
        self.flags.add_score_point(name, x=x, unique=unique, label_value=label_value)

    def get_score(self, name, get_x=True, ma=False):
        return self.scores.get_score(name, get_x=get_x, ma=ma)

    def get_folder(self):
        """Return the absolute path to the experiment folder."""
        return self.experiment_folder

    def get_exp_config_file(self):
        """Load or create the per-experiment config JSON."""
        if not os.path.exists(os.path.join(self.experiment_folder, "config.json")):
            self.set_exp_config_file({})
        config = json.load(open(os.path.join(self.experiment_folder, "config.json")))
        return config

    def get_exp_config_data(self, key):
        """Read a single key from the per-experiment config JSON."""
        return self.get_exp_config_file().get(key, None)

    def set_exp_config_file(self, config):
        """Write the per-experiment config JSON dict to disk."""
        with open(os.path.join(self.experiment_folder, "config.json"), "w") as f:
            json.dump(config, f, indent=4)

    def set_exp_config_data(self, key, value):
        """Update a single key in the per-experiment config file."""
        config = self.get_exp_config_file()
        config[key] = value
        self.set_exp_config_file(config)
