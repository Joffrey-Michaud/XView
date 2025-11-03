from xview.experiment import Experiment
import numpy as np
import time


# -------------------------------------------------------------------------------------
# Functions to generate random curves
def get_random_params():
    return {
        "amplitude": np.random.uniform(0.5, 3.0, 5),
        "frequency": np.random.uniform(0.1, 1.0, 5),
        "phase": np.random.uniform(0, 2 * np.pi, 5)
    }


def compute_y_value(x_t, params):
    return sum(params["amplitude"][i] * np.sin(params["frequency"][i] * x_t + params["phase"][i]) for i in range(5))


# --------------------------------------------------------------------------------------
# First step : init experiment
my_exp = Experiment("toy_example",  # give a name to the experiment
                    infos={"Sinusoid per curve": 5, "Amplitude range": (0.5, 3.0), "Frequency range": (0.1, 1.0), "Phase range": (0, 2 * np.pi)},  # you can add any information you want to the experiment in dict format
                    group="examples",  # possible to set a group for the experiment, to group them in one folder
                    clear=True
                    )

# Second step : set the status of the experiment to training (this line is mandatory)
my_exp.set_train_status()
print('start training')


points = np.linspace(0, 2 * np.pi, 200)

best_val = 100000

for i, x in enumerate(points):
    print(f"Iteration {i + 1}/{len(points)}")
    params_1 = get_random_params()
    params_2 = get_random_params()
    params_3 = get_random_params()

    y1 = compute_y_value(x, params_1)
    y2 = compute_y_value(x, params_2)
    y3 = compute_y_value(x, params_3)

    # Add a score to your experiment
    my_exp.add_score(
        name="Train_loss",  # Define the name
        x=x,  # The x value is not mandatory but if your x-Axis doesn't begin at 0, you can specify it
        y=y1,  # The y value is mandatory
        monitor="min"  # Specify if you want to monitor the min or the max of the curve (default is max)
    )

    # You can add as many score as you need
    my_exp.add_score(name="Val_loss", x=x, y=y2, monitor="max",
                     label_value=f"{y2:.3f}")  # You can add a label_value to the score to display it in the plot's legend, and update it dynamically

    # If desired, you can also pass plt_args to customize the plot appearance for the score (like marker, color, linestyle, etc.). It has to be a dict.
    my_exp.add_score(name="Test loss", x=x, y=y3, monitor="min,max,med,mean", plt_args={"marker": "x"})

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
