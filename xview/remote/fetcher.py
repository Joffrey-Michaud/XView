"""Remote job fetching utilities (placeholder).

This module is reserved for future helpers related to interacting with remote
execution backends (e.g., listing jobs, fetching results).
"""

from pathlib import Path
import subprocess
from xview import get_config_data


class RemoteFetcher:
    def __init__(self, host_name, login, exp_folder):
        self.host_name = host_name
        self.login = login
        self.remote_exp_folder = exp_folder
        self.local_exp_folder = get_config_data("data_folder")

    def sync_folders(self):
        rsync_command = [
            "rsync",
            "-azrL",
            f"{self.login}@{self.host_name}:{self.remote_exp_folder}/",
            f"{self.local_exp_folder}/"
        ]
        subprocess.run(rsync_command, check=True)

    # def get_remote_exp_mtime(self, exp_path):
    #     # récupérer les mtime d'une expérience dans exp_folder
    #     # convert exp_path to string if it's a Path object
    #     command_line = 'find "' + str(exp_path) + '" -type f -printf "%T@\n" | sort | tail -1'
    #     print("COMMANDE LINE :", command_line)
    #     stdout, stderr = self.exec_command_line(command_line)
    #     if stderr:
    #         print(f"Error retrieving mtime for {exp_path}: {stderr}")
    #         return None
    #     mtime_str = stdout.strip()
    #     try:
    #         mtime = float(mtime_str)
    #         return mtime
    #     except ValueError:
    #         print(f"Invalid mtime value for {exp_path}: {mtime_str}")
    #         return None

    # def open_ssh_connection(self):
    #     """Establish an SSH connection to the remote server."""
    #     ssh = paramiko.SSHClient()
    #     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #     ssh.connect(self.host_name, username=self.login)
    #     return ssh

    # def exec_command_line(self, command):
    #     if self.ssh is None:
    #         self.ssh = self.open_ssh_connection()
    #     # on travaille toujours  partir du dossier des exp
    #     command = f"cd {self.remote_exp_folder} && {command}"
    #     stdin, stdout, stderr = self.ssh.exec_command(command)
    #     return stdout.read().decode(), stderr.read().decode()

    # def get_remote_exp_paths(self):
    #     command_line = f'find . -type f -name "status.txt"'
    #     print("COMMANDE LINE :", command_line)
    #     stdout, stderr = self.exec_command_line(command_line)
    #     exp_paths = stdout.strip().split('\n')
    #     exp_paths = [Path(p).parent for p in exp_paths if p]
    #     return exp_paths
    
    # def get_local_exp_paths(self):
    #     exp_folder = Path(self.local_exp_folder)
    #     exp_paths = [p for p in exp_folder.glob('**/status.txt')]
    #     exp_paths = [p.parent for p in exp_paths]
    #     return exp_paths
