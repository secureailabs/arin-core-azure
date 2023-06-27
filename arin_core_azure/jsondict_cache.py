import hashlib
import json
import os

from arin_core_azure.file_store_azure import FileStoreAzure


class JsondictCache:
    def __init__(self, file_store: FileStoreAzure) -> None:
        self.file_store = file_store

    def hash_key(self, json_dict_key: dict) -> str:
        return hashlib.sha256(json.dumps(json_dict_key).encode("utf-8")).hexdigest()

    def get_file_name(self, jsondict_key: dict) -> str:
        return self.hash_key(jsondict_key) + ".json"

    def get_file_path_by_jsondict_key(self, jsondict_key: dict) -> str:
        file_name = self.get_file_name(jsondict_key)
        return self.file_store.get_file_path(file_name)

    def has(self, jsondict_key: dict) -> bool:
        file_name = self.get_file_name(jsondict_key)
        return self.file_store.has_file(file_name)

    def load_json(self, jsondict_key: dict) -> dict:
        file_name = self.get_file_name(jsondict_key)
        if not self.file_store.has_file(file_name):
            raise ValueError(f"File does not exist: {file_name}")
        path_file_value = self.file_store.get_file(file_name)
        with open(path_file_value, "r") as file:
            return json.load(file)

    def save_json(self, jsondict_key: dict, jsondict_value: dict) -> None:
        file_name = self.get_file_name(jsondict_key)
        path_file_value = self.file_store.get_file_path(file_name)
        with open(path_file_value, "w") as file:
            json.dump(jsondict_value, file, indent=4)
        self.file_store.upload_file(file_name)
