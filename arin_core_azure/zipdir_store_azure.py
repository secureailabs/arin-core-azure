import os

from arin_core_azure.env_tools import get_string_from_env
from arin_core_azure.file_store_azure import FileStoreAzure


class ZipdirStoreAzure(FileStoreAzure):
    def __init__(
        self,
        path_dir_zipcache: str,
        connectionstring: str,
        container_name: str,
    ) -> None:
        super().__init__(path_dir_zipcache, connectionstring, container_name)
