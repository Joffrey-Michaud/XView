from xview.experiment import Experiment
import numpy as np
import time


N_SIGNALS = 2

amplitudes = np.random.rand(N_SIGNALS)

infos = {f"A{i + 1}": amplitudes[i] for i in range(N_SIGNALS)}

my_exp = Experiment("colors_exp_2",  # give a name to the experiment
                    infos=infos,  # you can add any information you want to the experiment in dict format
                    group="debug_colors",  # possible to set a group for the experiment, to group them in one folder
                    clear=True
                    )

my_exp.set_train_status()  # set the status of the experiment to training

points = np.linspace(0, 3 * np.pi, 300)

best_val_1 = 100000
best_val_5 = 100000

for i, x in enumerate(points):
    for j in range(N_SIGNALS):
        y = amplitudes[j] * np.sin(x + j + 1)
        my_exp.add_score(name=f"Signal_{j + 1}", x=x, y=y)  # add a score with x and y values. The x value is not mandatory, you can add only y values

        if j == 1 and y < best_val_1:
            best_val_1 = y
            my_exp.add_flag(name="S2 best", x=x, unique=True, label_value=f"{best_val_1:.3f}")

        if j == 5 and y < best_val_5:
            best_val_5 = y
            my_exp.add_flag(name="S6 best", x=x, unique=True, label_value=f"{best_val_5:.3f}")

    if i == 100:
        my_exp.add_flag(name="Premier tier", x=x, unique=True, label_value=i)
    if i == 200:
        my_exp.add_flag(name="Second tier", x=x, unique=True, label_value=i)

    # time.sleep(1)

# my_exp.set_finished_status()  # set the status of the experiment to finished
