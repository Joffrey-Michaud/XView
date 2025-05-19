from xview.experiment import Experiment
import numpy as np


A1,A2, A3 = np.random.rand(3)

my_exp = Experiment("toy_experiment_3",  # give a name to the experiment
                    infos={"A1": A1, "A2": A2, "A3": A3},  # you can add any information you want to the experiment in dict format
                    group="examples_group",  # possible to set a group for the experiment, to group them in one folder
                    clear=True
                    )

my_exp.set_train_status()  # set the status of the experiment to training

points = np.linspace(0, 2 * np.pi, 200)

best_val = 100000

for i, x in enumerate(points):
    y1 = A1 * np.sin(x + 1)
    y2 = A2 * np.sin(x + 2)
    y3 = A3 * np.sin(x + 3)

    my_exp.add_score(name="Train_loss", x=x, y=y1, plt_args={"lw": 5})  # add a score with x and y values. The x value is not mandatory, you can add only y values
    my_exp.add_score(name="Val_loss", x=x, y=y2)  # 
    my_exp.add_score(name="Test_loss", x=x, y=y3)  # 

    if i in [50, 75, 150]:
        my_exp.add_flag(name="flag_1", x=x)  # add a flag at specific points. It will be displayedd with vertical lines in the plot

    if y2 < best_val:
        best_val = y2
        print(f"New best val: {best_val} at x={x}")
        my_exp.add_flag(name="best_val", x=x, unique=True, label_value=best_val)  # add a flag with unique=True to keep only the last one

# my_exp.set_finished_status()  # set the status of the experiment to finished