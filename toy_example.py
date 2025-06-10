from xview.experiment import Experiment
import numpy as np
import time


A1, A2, A3 = np.random.rand(3)

my_exp = Experiment("toy_example",  # give a name to the experiment
                    infos={"A1": A1, "A2": A2, "A3": A3},  # you can add any information you want to the experiment in dict format
                    group="examples",  # possible to set a group for the experiment, to group them in one folder
                    clear=True
                    )

# Set the status of the experiment to training (this line is mandatory)
my_exp.set_train_status()

points = np.linspace(0, 2 * np.pi, 200)

best_val = 100000

for i, x in enumerate(points):
    y1 = A1 * np.sin(x + 1)
    y2 = A2 * np.sin(x + 2)
    y3 = A3 * np.sin(x + 3)

    # add a score with x and y values. The x value is not mandatory, you can add only y values if you want
    my_exp.add_score(name="Train_loss", x=x, y=y1)

    # You can add a label_value to the score to display it in the plot's legend, and update it dynamically
    my_exp.add_score(name="Val_loss", x=x, y=y2, label_value=f"{y2:.3f}")

    # If desired, you can also pass plt_args to customize the plot appearance for the score (like marker, color, linestyle, etc.). It has to be a dict.
    my_exp.add_score(name="Test loss", x=x, y=y3, plt_args={"marker": "x"})

    # You can add a flag, which will be displayed in the plot as a vertical line at the x value, with a label_value to display in the legend, and update it dynamically :
    if y2 < best_val:
        best_val = y2
        my_exp.add_flag(name="best_val", x=x, unique=True, label_value=f"{best_val:.3f}")

    # If you want to set up a flag that will be displayed multiple times, you can do it like this:
    if i % 100 == 50 and i != 0:
        my_exp.add_flag(name="Multiples of 50", x=x, unique=False)

    # You can add info on the experiment at any time, which will be displayed in the info tab of the experiment:
    my_exp.set_info("Current iteration", value=i)

    time.sleep(0.25)

# Set the status of the experiment to training. This line is mandatory to indicate that the training is finished, otherwise the experiment will be considered as running.
my_exp.set_finished_status()
