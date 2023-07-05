from typing import List

import paramiko


class SshHelper:
    def __init__(
        self,
        hostname: str,
        username: str,
        path_keyfile_host: str,
        verbose=True,
    ) -> None:

        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(hostname=hostname, username=username, key_filename=path_keyfile_host)
        self.verbose = verbose

    # def scp_get_client(
    #     hostname: str,
    #     username: str,
    #     path_keyfile_host: str,
    # ):
    #     """
    #     this is a wrapper around paramiko.SSHClient
    #     """
    #     client = paramiko.SSHClient()
    #     client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #     client.connect(hostname=hostname, username=username, key_filename=path_keyfile_host)
    #     return client
    def run_remote(self, command: str, path: str = "/"):
        if self.verbose:
            print("Running command: ")
            print(command)

        # Execute the command
        stdin, stdout, stderr = self.ssh_client.exec_command("cd " + path + " && " + command, get_pty=True)
        # Read and print the output
        if self.verbose:
            output = stdout.read().decode("utf-8")
            print(output)

            # Print any errors
            error = stderr.read().decode("utf-8")
            if error:
                print("Error:")
                print(error)

    def install_remote(self, list_package: List[str], do_update: bool = True):
        if do_update:
            self.run_remote("sudo apt-get update")
            self.run_remote("sudo apt-get upgrade")
        self.run_remote("sudo apt install -y " + " ".join(list_package))

    def clone_remote_with_token(self, git_url: str, git_token: str, branch_name: str = "main"):
        self.run_remote(
            f"git clone -b {branch_name} https://{git_token}@{git_url}", path="~/"
        )  # TODO for some reason this does not quite work
