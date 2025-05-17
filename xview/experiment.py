import os
from xview.utils.utils import *
from xview.score import MultiScores
import shutil


class Experiment(object):
    def __init__(self, name, infos=None, group=None, clear=None):
        self.name = name
        self.group = group

        #  chemin vers le fichier de config
        curr_dir = os.path.abspath(os.path.dirname(__file__))
        config_path = os.path.join("config", "config.json")
        abs_config_path = os.path.join(curr_dir, config_path)

        # lecture du fichier de config et création du dossier de l'expérience
        self.data_folder = read_json(abs_config_path)["data_folder"]

        if self.group is not None:
            self.data_folder = os.path.join(self.data_folder, self.group)

        self.experiment_folder = os.path.join(self.data_folder, self.name)

        if clear == True and os.path.exists(self.experiment_folder):
            shutil.rmtree(self.experiment_folder)

        os.makedirs(self.experiment_folder, exist_ok=True)

        # créer le fichier d'infos si donné
        self.infos = infos
        if infos is not None:
            self.exp_infos_file = os.path.join(self.experiment_folder, "exp_infos.json")
            write_json(self.exp_infos_file, infos)

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

    def set_train_status(self):
        self.update_status("training")

    def set_finished_status(self):
        self.update_status("finished")

    def update_status(self, status):
        self.status = status
        write_file(self.status_file, self.status, flag="w")

    def add_training_score(self, score):
        write_file(self.score_file_training, str(score), flag="a")

    def add_validation_score(self, score):
        write_file(self.score_file_validation, str(score), flag="a")

    def add_score(self, name, y, x=None):
        if name not in self.scores.scores:
            self.scores.add_score(name)
        self.scores.add_score_point(name, y, x)

    def add_flag(self, name, x=None, unique=False):
        if name not in self.flags.scores:
            self.flags.add_score(name)
        if x is None:
            x = max(len(self.scores), len(self.flags))
        self.flags.add_score_point(name, x=x, unique=unique)
