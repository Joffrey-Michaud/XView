import os


def get_metrics(exp_folder):
    scores_folder = os.path.join(exp_folder, "scores")
    scores_files = os.listdir(scores_folder)
    # garder uniquement les dossiers
    metrics = [f.replace(".txt", "") for f in sorted(scores_files)]
    return metrics