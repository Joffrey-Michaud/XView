import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from config import config_exists


# 📁 Chemins de base
# APP_DIR = os.path.dirname(f"{os.path.expanduser('~')}/.xview/")
APP_DIR = Path.home() / ".xview"
EXEC_DIR = Path(__file__).resolve().parent

VENV_DIR = APP_DIR / "xview_ven"
REQUIREMENTS_FILE = EXEC_DIR / "requirements.txt"
SCRIPT_FILE = EXEC_DIR / "xview_gui.py"


def create_venv():
    if VENV_DIR.exists():
        print("Virtual environment 'xview_venv' already exists.")
    else:
        print("Creating virtual environment 'xview_venv'...")
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV_DIR)])
        print("Virtual environment created.")

    python_bin = VENV_DIR / ("Scripts" if platform.system() == "Windows" else "bin") / "python"
    print("Installing dependencies...")
    subprocess.check_call([str(python_bin), "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)])
    print("Dependencies installed.")

def create_venv_wsl():
    if VENV_DIR.exists():
        print("Virtual environment 'xview_venv' already exists.")
    else:
        print("Creating virtual environment 'xview_venv'...")
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV_DIR)])
        print("Virtual environment created.")

    python_bin = VENV_DIR / ("Scripts" if platform.system() == "Windows" else "bin") / "python"
    print("Installing dependencies...")
    # lire le requirements.txt dans le répertoire courant et remplacer "PyQt5" par "PyQt5==5.15.2"
    with open(REQUIREMENTS_FILE, 'r') as f:
        requirements = f.readlines()
    requirements = [line.replace("PyQt5", "PyQt5==5.15.2") for line in requirements]
    with open(REQUIREMENTS_FILE, 'w') as f:
        f.writelines(requirements)
    subprocess.check_call([str(python_bin), "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)])
    print("Dependencies installed.")


def is_in_path(directory):
    path_env = os.environ.get("PATH", "")
    return any(Path(p).resolve() == Path(directory).resolve() for p in path_env.split(os.pathsep))


def install_launcher_linux():
    target_dir = Path.home() / ".local" / "bin"
    target_dir.mkdir(parents=True, exist_ok=True)

    python_bin = VENV_DIR / "bin" / "python"

    launcher = target_dir / "xview"
    with open(launcher, "w") as f:
        f.write(f"""#!/bin/bash
source "{VENV_DIR}/bin/activate"
"{python_bin}" "{SCRIPT_FILE}"
""")
    launcher.chmod(0o755)

    if not is_in_path(target_dir):
        print("⚠️ The ~/.local/bin directory is not in your PATH.")
        print("Add this line to your ~/.bashrc or ~/.zshrc:")
        print('export PATH="$HOME/.local/bin:$PATH"')


def install_launcher_windows():
    windows_apps = Path(os.environ["USERPROFILE"]) / "AppData" / "Local" / "Microsoft" / "WindowsApps"
    fallback_dir = Path(os.environ["USERPROFILE"]) / "xview_launcher"
    fallback_dir.mkdir(exist_ok=True)

    bat_file = fallback_dir / "xview.bat"
    with open(bat_file, "w") as f:
        f.write(f"""@echo off
call "{VENV_DIR}\\Scripts\\activate.bat"
python "{SCRIPT_FILE}"
""")

    # print(f"✅ Script .bat créé dans {bat_file}")

    try:
        if windows_apps.exists():
            shutil.copy(bat_file, windows_apps / "xview.bat")
            print(f"✅ Script copied to {windows_apps}")
        else:
            print("⚠️ WindowsApps folder not found. Manually add this folder to your PATH:")
            print(f"{fallback_dir}")
    except PermissionError:
        print("❌ Permission denied. Run as administrator or manually copy this file to a folder in your PATH.")


def is_wsl():
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except FileNotFoundError:
        return False

def main():
    print("Welcome to the XView installer!")
    print("This script will set up a virtual environment and install the necessary dependencies for XView.")
    print("Type 'y' to continue or 'n' to exit.")
    choice = input("Continue ? (y/n) : ").strip().lower()
    while choice not in ('y', 'n'):
        print("Please enter 'y' or 'n'.")
        choice = input("Continue ? (y/n) : ").strip().lower()
    if choice == 'n':
        print("Installation annulée.")
        return

    current_os = platform.system()
    if current_os == "Linux":
        if is_wsl():
            create_venv_wsl()
        else:
            create_venv()
            install_launcher_linux()

    elif current_os == "Windows":
        create_venv()
        install_launcher_windows()
    else:
        print(f"Unsupported OS : {current_os}")

    if not os.path.isfile(APP_DIR / "config.json"):
        config_script = EXEC_DIR / "config.py"
        python_bin = VENV_DIR / ("Scripts" if platform.system() == "Windows" else "bin") / "python"
        subprocess.run([str(python_bin), str(config_script)])

    print("Installation finished.")
    print("You can now run XView by typing 'xview' in your terminal.")


if __name__ == "__main__":
    main()
