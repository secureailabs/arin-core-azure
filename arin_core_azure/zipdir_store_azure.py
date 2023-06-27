import os

from arin_core_azure.file_store_azure import FileStoreAzure


class ZipDirStoreAzure(FileStoreAzure):
    def __init__(self, path_dir_zipcache: str) -> None:
        super().__init__(path_dir_zipcache)
