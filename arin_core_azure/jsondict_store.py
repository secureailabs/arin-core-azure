import hashlib
import json
import os
from typing import List

from arin_core_azure.file_store_azure import FileStoreAzure


class JsondictStore:
    def __init__(self, file_store: FileStoreAzure) -> None:
        self.file_store = file_store

    def hash_key(self, json_dict_key: dict) -> str:
        return hashlib.sha256(json.dumps(json_dict_key).encode("utf-8")).hexdigest()

    def has_key_for_dict(self, jsondict_key: dict) -> bool:
        file_name = self.get_file_name_for_dict(jsondict_key)
        return self.file_store.has_file(file_name)

    def has_key(self, key: str) -> bool:
        file_name = self.get_file_name(key)
        return self.file_store.has_file(file_name)

    def list_key(self) -> List[str]:
        list_key = [file_name[:-5] for file_name in self.file_store.list_key()]
        return list_key

    def get_file_name(self, key: str) -> str:
        return key + ".json"

    def get_file_name_for_dict(self, jsondict_key: dict) -> str:
        return self.get_file_name(self.hash_key(jsondict_key))

    def get_file_path_for_jsondict_key(self, jsondict_key: dict) -> str:
        file_name = self.get_file_name_for_dict(jsondict_key)
        return self.file_store.get_file_path(file_name)

    def load_json_for_dict(self, jsondict_key: dict) -> dict:
        file_name = self.get_file_name_for_dict(jsondict_key)
        if not self.file_store.has_file(file_name):
            raise ValueError(f"File does not exist: {file_name}")
        path_file_value = self.file_store.get_file(file_name)
        with open(path_file_value, "r") as file:
            return json.load(file)

    def load_json(self, key: str) -> dict:
        file_name = self.get_file_name(key)
        if not self.file_store.has_file(file_name):
            raise ValueError(f"File does not exist: {file_name}")
        path_file_value = self.file_store.get_file(file_name)
        with open(path_file_value, "r") as file:
            return json.load(file)

    def save_json_for_dict(self, jsondict_key: dict, jsondict_value: dict) -> None:
        file_name = self.get_file_name_for_dict(jsondict_key)
        path_file_value = self.file_store.get_file_path(file_name)
        with open(path_file_value, "w") as file:
            json.dump(jsondict_value, file, indent=4)
        self.file_store.upload_file(file_name)

    def save_json(self, key: str, jsondict_value: dict) -> None:
        file_name = self.get_file_name(key)
        path_file_value = self.file_store.get_file_path(file_name)
        with open(path_file_value, "w") as file:
            json.dump(jsondict_value, file, indent=4)
        self.file_store.upload_file(file_name)

    def delete_json_for_dict(self, jsondict_key: dict) -> None:
        file_name = self.get_file_name_for_dict(jsondict_key)
        self.file_store.delete_file(file_name)
