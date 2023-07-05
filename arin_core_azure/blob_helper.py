
import os
import sys
import tqdm
from typing import Optional

from azure.storage.blob import BlobServiceClient
from azure.storage.blob import BlobClient
from azure.storage.blob import ContainerClient

from arin_core_azure.base_helper import BaseHelper
import hashlib

class BlobHelper(BaseHelper):

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> None:
        super().__init__(client_id, client_secret, tenant_id)

    # def get_connection_string(self) -> str:
    #     account_name = "arindemo"
    #     account_key = "
    #     return f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.account_key};EndpointSuffix=core.windows.net"

    # def list_container(self) -> None:
    #     account_url = "https://<account_name>.blob.core.windows.net"
    #     blob_service_client = BlobServiceClient(credential=self.credential, account_url=self.account_url)
    #     list_container = self.blob_service_client.list_containers()
    #     for container_properties in self.blob_service_client.list_containers():
    #         print(container_properties.name)

    def compute_etag(self, path_file: str) -> str:
        block_size = 4 * 1024 * 1024  # 4MB, change this value as per your requirements
        sha256 = hashlib.sha256()

        with open(path_file, 'rb') as file:
            while True:
                data = file.read(block_size)
                if not data:
                    break
                sha256.update(data)

        return sha256.hexdigest()

    def download_blob_to_file(
        self,
        blob_client: BlobClient,
        path_file: str,
        *,
        create_dir_parent: bool = True,
        verbose: bool = False,
    ) -> None:
        if not blob_client.exists():
            raise ValueError(f"blob does not exist:  {blob_client.blob_name}")

        # check if parent directory exists
        path_dir_parent = os.path.dirname(path_file)
        if not os.path.isdir(path_dir_parent):
            if create_dir_parent:
                if verbose:
                    print(f"Parent directory does not exist creating directory:  {path_dir_parent}")
                os.makedirs(path_dir_parent)
            else:
                raise ValueError(f"directory does not exist:  {path_dir_parent}")

        # check if download is actually needed
        if os.path.isfile(path_file):
            etag_file = self.compute_etag(path_file)
            etag_blob = blob_client.get_blob_properties().etag
            if etag_file == etag_blob:
                if verbose:
                    print(f"file {path_file} already exists and has same etag:  {etag_file}, skipping download")
                return

        # do the actual download
        if verbose:
            print(f"Downloading blob:  {blob_client.blob_name}")
            with open(path_file, 'wb') as file:
                download_size:int = blob_client.get_blob_properties().size # type: ignore
                download_size_mb = download_size / (1024 * 1024)
                bytes_downloaded = 0
                with tqdm(total=download_size_mb, unit='MB', file=sys.stdout) as progress_bar:
                    while bytes_downloaded < download_size:
                        data = blob_client.download_blob(offset=bytes_downloaded) #TODO make paged version as well
                        chunk = data.readall()
                        file.write(chunk)
                        bytes_downloaded += len(chunk)
                        progress_bar.update(len(chunk) / (1024 * 1024))
        else:
            with open(path_file, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())




    def upload_file(self, file_name: str) -> None:
        # TODO check hashe
        # TODO make verbose
        path_file = self.get_file_path(file_name)
        if not os.path.isfile(path_file):
            raise Exception(f"file does not exist:  {file_name}")
        blob_client = self.container_client.get_blob_client(file_name)
        with open(path_file, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)










    # some code to deal with aws etags can be found at https://github.com/kozzion/breaker_aws/blob/main/breaker_aws/system_s3.py:is_different
    def upload_dir(self, container_client, path_dir_source, *, type_overide:str="overide_all", delete_excess:bool=False):
        if not type_overide in ["overide_all", "overide_different", "overide_none"]:
            raise ValueError(f"unknown type_overide {type_overide}")
        list_blob_keep = []
        for path_dir, _, list_name_file in os.walk(path_dir_source, topdown=False):
            for name_file in list_name_file:
                path_file = os.path.join(path_dir, name_file)
                name_blob = os.path.join(path_dir, name_file)[len(path_dir_source):]
                list_blob_keep.append(name_blob)
                blob_client = container_client.get_blob_client(name_blob)
                if blob_client.exists():
                    if type_overide == "overide_none":
                        continue
                    if type_overide == "overide_different":
                        raise NotImplementedError()
                else:
                    with open(path_file, "rb") as file:
                        container_client.get_blob_client(name_blob).upload_blob(file)
        if delete_excess:
            for blob_properties in container_client.list_blobs():
                if not blob_properties["name"] in list_blob_keep:
                    blob_client = container_client.get_blob_client(blob_properties["name"])
                    blob_client.delete_blob()


    def download_dir(self, container_client, path_dir_target, *, type_overide:str="overide_all", delete_excess:bool=False, bytes_max=-1):
        if not type_overide in ["overide_all", "overide_different", "overide_none"]:
            raise ValueError(f"unknown type_overide {type_overide}")
        list_path_file_keep = []
        for blob_properties in container_client.list_blobs():
            name_blob = blob_properties["name"]
            blob_client = container_client.get_blob_client(name_blob)
            list_path_blob = name_blob.split("/")
            path_file = path_dir_target
            for path_blob in list_path_blob:
                path_file = os.path.join(path_file, path_blob)
            list_path_file_keep.append(path_file)

            if os.path.isfile(path_file):
                if type_overide == "overide_none":
                    continue
                if type_overide == "overide_different":
                    raise NotImplementedError()
            path_dir_parent = os.path.dirname(path_file)
            if not os.path.isdir(path_dir_parent):
                os.makedirs(path_dir_parent)
            with open(path_file, "wb") as file:
            download_stream = blob_client.download_blob()
            file.write(download_stream.readall())

        if delete_excess:
            raise NotImplementedError()

