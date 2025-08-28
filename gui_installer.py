import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


APP_DIR = Path.home() / ".xview"
EXEC_DIR = Path(__file__).resolve().parent

REQUIREMENTS_FILE = EXEC_DIR / "requirements.txt"
SCRIPT_FILE = EXEC_DIR / "xview_gui.py"

def is_in_path(directory):
    path_env = os.environ.get("PATH", "")
    return any(Path(p).resolve() == Path(directory).resolve() for p in path_env.split(os.pathsep))


def install_launcher_linux():
    target_dir = Path.home() / ".local" / "bin"
    target_dir.mkdir(parents=True, exist_ok=True)

    python_cmd = sys.executable  # Use the current Python env (robust for WSL/conda)
    launcher = target_dir / "xview"
    with open(launcher, "w") as f:
        f.write(
            f"""#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="$HOME/.xview"
LOG_FILE="$LOG_DIR/xview.log"
mkdir -p "$LOG_DIR"
touch "$LOG_FILE"

# Start fully detached and append logs (works on Ubuntu & WSL2)
if command -v setsid >/dev/null 2>&1; then
    setsid -f "{python_cmd}" "{SCRIPT_FILE}" >> "$LOG_FILE" 2>&1 < /dev/null
else
    nohup "{python_cmd}" "{SCRIPT_FILE}" >> "$LOG_FILE" 2>&1 < /dev/null &
fi

exit 0
"""
        )
    launcher.chmod(0o755)

    if not is_in_path(target_dir):
        print("WARNING: The ~/.local/bin directory is not in your PATH.")
        print("Add this line to your ~/.bashrc or ~/.zshrc:")
        print('export PATH="$HOME/.local/bin:$PATH"')


def install_launcher_windows():
    windows_apps = Path(os.environ["USERPROFILE"]) / "AppData" / "Local" / "Microsoft" / "WindowsApps"
    fallback_dir = Path(os.environ["USERPROFILE"]) / "xview_launcher"
    fallback_dir.mkdir(exist_ok=True)

    log_file = APP_DIR / "xview.log"
    pythonw = Path(sys.exec_prefix) / "pythonw.exe"  # Python sans console
    bat_file = fallback_dir / "xview.bat"
    with open(bat_file, "w") as f:
        f.write(f"""@echo off
setlocal ENABLEDELAYEDEXPANSION
if not exist "{APP_DIR}" mkdir "{APP_DIR}"
if not exist "{log_file}" type nul > "{log_file}" 2>nul
start "" "{pythonw}" "{SCRIPT_FILE}" >> "{log_file}" 2>&1
exit /b 0
""")

    try:
        if windows_apps.exists():
            shutil.copy(bat_file, windows_apps / "xview.bat")
            print(f"Script copied to {windows_apps}")
        else:
            print("WARNING/ WindowsApps folder not found. Manually add this folder to your PATH:")
            print(f"{fallback_dir}")
    except PermissionError:
        print("Permission denied. Run as administrator or manually copy this file to a folder in your PATH.")


def is_wsl():
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except FileNotFoundError:
        return False


def main():
    current_os = platform.system()
    if current_os == "Linux":
        install_launcher_linux()

    elif current_os == "Windows":
        install_launcher_windows()
    else:
        print(f"Unsupported OS : {current_os}")

    if not os.path.isfile(APP_DIR / "config.json"):
        config_script = EXEC_DIR / "config.py"
        subprocess.run([sys.executable, str(config_script)])

    print("Installation finished.")
    print("You can now run XView by typing 'xview' in your terminal.")


if __name__ == "__main__":
    main()
