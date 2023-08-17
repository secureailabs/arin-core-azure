from arin_core_azure.env_tools import get_string_from_file_from_env
from arin_core_azure.ssh_helper import SshHelper

username = "azureuser"

# hostname = "20.236.63.122"
# path_keyfile_host = "C:\\key\\gpu-machine-jaap-0_key.pem"
# git_url = "github.com/secureailabs/arin-core-azure.git"

hostname = "20.83.235.179"
path_keyfile_host = "C:\\key\\jaap-workspace-key.pem"
git_url = "github.com/secureailabs/green-team.git"

git_token = get_string_from_file_from_env("PATH_FILE_GIT_TOKEN")
ssh_helper = SshHelper(
    hostname,
    username,
    path_keyfile_host,
    verbose=True,
)

ssh_helper.clone_remote_with_token(git_url, git_token)
