import subprocess
import functools
import os

_warned_once = False

def is_up_to_date() -> bool:
    """Vérifie si le dépôt local est à jour avec la branche distante."""
    REPO_DIR = os.path.dirname(os.path.abspath(__file__))
    try:
        subprocess.run(["git", "fetch"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, cwd=REPO_DIR)

        local = subprocess.check_output(["git", "rev-parse", "@"], stderr=subprocess.PIPE, cwd=REPO_DIR).strip()
        remote = subprocess.check_output(["git", "rev-parse", "@{u}"], stderr=subprocess.PIPE, cwd=REPO_DIR).strip()
        base = subprocess.check_output(["git", "merge-base", "@", "@{u}"], stderr=subprocess.PIPE, cwd=REPO_DIR).strip()

        return local == remote
    except subprocess.CalledProcessError as e:
        print("/!\\ Erreur lors de la vérification de la version.")
        print(e.stderr.decode())
        return True  # Par sécurité : éviter de bloquer l'exécution
    except Exception as e:
        print(f"/!\\ Erreur inattendue : {e}")
        return True


def warn_if_outdated(obj):
    @functools.wraps(obj)
    def wrapper(*args, **kwargs):
        global _warned_once
        if not _warned_once and not is_up_to_date():
            print("# -------------------------------------------------------------------------- #")
            print("Votre version du projet XView n'est pas à jour. Vous pouvez le mettre à jour en exécutant 'git pull' dans le répertoire du projet.")
            print("# -------------------------------------------------------------------------- #")
            _warned_once = True
        return obj(*args, **kwargs)
    return wrapper


def pull_latest_changes():
    """Effectue un git pull pour récupérer les dernières modifications."""
    try:
        REPO_DIR = os.path.dirname(os.path.abspath(__file__))
        subprocess.run(["git", "pull"], check=True, cwd=REPO_DIR)
        print("Projet mis à jour avec succès.")
    except subprocess.CalledProcessError:
        print("/!\\ Échec du git pull.")

