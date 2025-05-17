import os
from xview.utils.utils import write_file

class Score(object):
    def __init__(self, name, score_dir):
        self.name = name
        self.score_dir = score_dir
        self.score_file = os.path.join(self.score_dir, f"{self.name}.txt")

    def add_score_point(self, x=None, y=None, unique=False):
        if x is not None and y is not None:
            line = f"{x},{y}"
        elif x is not None:
            line = f"{x}"
        elif y is not None:
            line = f"{y}"

        write_file(self.score_file, line, flag="a" if not unique else "w")


class MultiScores(object):
    def __init__(self, score_dir):
        self.score_dir = score_dir
        self.scores = {}

    def add_score(self, name):
        if name not in self.scores:
            self.scores[name] = Score(name, self.score_dir)
        
    def add_score_point(self, name, x=None, y=None, unique=False):
        assert name in self.scores, f"Score {name} not found. Please add it first."
        self.scores[name].add_score_point(y, x, unique=unique)


        