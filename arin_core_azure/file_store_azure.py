import os

from azure.storage.blob import BlobServiceClient

class FileStoreAzure:
    def __init__(self, path_dir_cache: str, container_name: str) -> None:
        if path_dir_cache == None:
            raise ValueError("path_dir_cache is None")
        if container_name == None:
            raise ValueError("container_name is None")

        self.path_dir_cache = path_dir_cache
        self.container_name = container_name

        if not os.path.isdir(self.path_dir_cache):
            os.makedirs(self.path_dir_cache)

        self.connection_string = os.environ["AZURE_CONNECTIONSTRING_DATASETS"]
        if self.connection_string is None:
            raise ValueError("AZURE_CONNECTIONSTRING_DATASETS is not set")

        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        # Check if the container exists
        self.container_client = self.blob_service_client.get_container_client(self.container_name)

        if self.container_client.exists():
            print(f"The container '{self.container_name}' exists.")
        else:
            print(f"The container '{self.container_name}' does not exist, creating.")
            self.blob_service_client.create_container(self.container_name)
            print(f"The container '{self.container_name}' has been created.")

    def get_file_path(self, file_name):
        return os.path.join(self.path_dir_cache, file_name)

    def has_file(self, file_name: str) -> bool:
        path_file = self.get_file_path(file_name)
        if os.path.isfile(path_file):
            return True
        blob_client = self.container_client.get_blob_client(file_name)
        return blob_client.exists()

    def get_file(
        self,
        file_name: str,
    ) -> str:
        if not self.has_file(file_name):
            raise Exception(f"file does not exist:  {file_name}")
        path_file = self.get_file_path(file_name)
        if not os.path.isfile(path_file):
            self.download_file(file_name)
        return path_file

    def download_file(
        self,
        file_name: str,
    ) -> None:
        # TODO check hash
        # TODO make verbose
        path_file = self.get_file_path(file_name)
        blob_client = self.container_client.get_blob_client(file_name)
        with open(path_file, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

    def upload_file(self, file_name: str) -> None:
        # TODO check hash
        # TODO make verbose
        path_file = self.get_file_path(file_name)
        if not os.path.isfile(path_file):
            raise Exception(f"file does not exist:  {file_name}")
        blob_client = self.container_client.get_blob_client(file_name)
        with open(path_file, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
