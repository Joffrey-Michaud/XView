import os
from xview.utils.utils import write_file, write_json, compute_moving_average


class Score(object):
    def __init__(self, name, score_dir, plt_args: dict = None):
        self.name = name
        self.score_dir = score_dir
        self.score_file = os.path.join(self.score_dir, f"{self.name}.txt")
        self.plt_args = plt_args
        if self.plt_args is not None:
            plt_args_file = os.path.join(self.score_dir, f"{self.name}_plt_args.json")
            write_json(plt_args_file, self.plt_args)

    def add_score_point(self, x=None, y=None, unique=False, label_value=None):
        if x is not None and y is not None:
            line = f"{x},{y}"
        elif x is not None:
            line = f"{x}"
        elif y is not None:
            line = f"{y}"

        write_file(self.score_file, line, flag="a" if not unique else "w")

        if label_value is not None:
            label_file = os.path.join(self.score_dir, f"{self.name}_label_value.txt")
            write_file(label_file, label_value, flag="w")

    def __len__(self):
        if os.path.exists(self.score_file):
            with open(self.score_file, "r") as f:
                lines = f.readlines()
            return len(lines)
        else:
            return 0

    def read_scores(self, get_x: bool = True, ma=False):
        """Lit les scores à partir d'un fichier et retourne une liste de tuples (x, y)."""
        if os.path.exists(self.score_file):
            with open(self.score_file, "r") as f:
                lines = f.readlines()
            x = []
            y = []
            for line in lines:
                values = line.strip().split(",")
                if len(values) == 1:
                    y.append(float(values[0]))
                else:
                    x.append(float(values[0]))
                    y.append(float(values[1]))
            if ma is not None and ma is not False:
                window = ma if not isinstance(ma, bool) else 15
                y = compute_moving_average(y, window)
            if get_x:
                return (x, y)
            return y

        else:
            print(f"Le fichier {self.score_file} n'existe pas.")
            return []


class MultiScores(object):
    def __init__(self, score_dir):
        self.score_dir = score_dir
        self.scores: dict[str, Score] = {}

    def add_score(self, name, plt_args=None):
        if name not in self.scores:
            self.scores[name] = Score(name, self.score_dir, plt_args=plt_args)

    def get_max_len(self):
        max_len = 0
        for score in self.scores.values():
            max_len = max(max_len, len(score))
        return max_len

    def __len__(self):
        return self.get_max_len()

    def add_score_point(self, name, x=None, y=None, unique=False, label_value=None):
        assert name in self.scores, f"Score {name} not found. Please add it first."
        self.scores[name].add_score_point(y, x, unique=unique, label_value=label_value)

    def get_score(self, name, get_x=True, ma=False):
        assert name in self.scores, f"Score {name} not found."
        score = self.scores[name].read_scores(get_x=get_x, ma=ma)
        return score
