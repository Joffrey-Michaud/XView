import os
from xview.utils.utils import *
from xview.score import MultiScores
import shutil
from xview.update.update_project import warn_if_outdated
from xview import get_config_data


@warn_if_outdated
class Experiment(object):
    def __init__(self, name, infos=None, group=None, clear=None):
        self.name = name
        self.group = group

        # lecture du fichier de config et création du dossier de l'expérience
        self.data_folder = get_config_data("data_folder")

        if self.group is not None:
            self.data_folder = os.path.join(self.data_folder, self.group)

        self.experiment_folder = os.path.join(self.data_folder, self.name)

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

    def get_infos(self):
        if os.path.exists(self.infos_path):
            self.infos = read_json(self.infos_path)
        else:
            self.infos = {}
            self.set_infos({})
        return self.infos

    def set_infos(self, infos):
        self.infos = infos
        if infos is not None:
            write_json(self.infos_path, infos)

    def set_info(self, key, value):
        self.infos[key] = value
        write_json(self.infos_path, self.infos)

    def set_train_status(self):
        self.update_status("training")

    def set_finished_status(self):
        self.update_status("finished")

    def update_status(self, status):
        self.status = status
        write_file(self.status_file, self.status, flag="w")

    def add_score(self, name, y, x=None, plt_args: dict = None, label_value=None):
        if name not in self.scores.scores:
            self.scores.add_score(name, plt_args=plt_args)
        self.scores.add_score_point(name, y, x, label_value=label_value)

    def add_flag(self, name, x=None, unique=False, plt_args: dict = None, label_value=None):
        if name not in self.flags.scores:
            self.flags.add_score(name, plt_args=plt_args)
        if x is None:
            x = max(len(self.scores), len(self.flags))
        self.flags.add_score_point(name, x=x, unique=unique, label_value=label_value)
