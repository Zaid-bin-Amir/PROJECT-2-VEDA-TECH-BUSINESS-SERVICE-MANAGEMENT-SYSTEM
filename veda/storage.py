import json
import os
import shutil

from .constants import COLLECTIONS
from .exceptions import StorageError


class DataStore:
    def __init__(self, path, seed_path=None):
        self.path = path
        self.seed_path = seed_path
        self.data = {name: [] for name in COLLECTIONS}
        self.load()

    def load(self):
        if not os.path.exists(self.path):
            self.restore_seed()
        if not os.path.exists(self.path):
            self.data = {name: [] for name in COLLECTIONS}
            self.save()
            return
        try:
            with open(self.path, "r", encoding="utf-8") as handle:
                loaded = json.load(handle)
        except (json.JSONDecodeError, OSError) as error:
            raise StorageError(f"Could not read data file: {error}")
        if not isinstance(loaded, dict):
            raise StorageError("Data file has an invalid structure.")
        for name in COLLECTIONS:
            records = loaded.get(name, [])
            if not isinstance(records, list):
                raise StorageError(f"Collection '{name}' must be a list.")
            self.data[name] = records

    def save(self):
        directory = os.path.dirname(os.path.abspath(self.path))
        os.makedirs(directory, exist_ok=True)
        temp_path = self.path + ".tmp"
        try:
            with open(temp_path, "w", encoding="utf-8") as handle:
                json.dump(self.data, handle, indent=2, ensure_ascii=False)
            os.replace(temp_path, self.path)
        except OSError as error:
            raise StorageError(f"Could not save data file: {error}")

    def restore_seed(self):
        if not self.seed_path or not os.path.exists(self.seed_path):
            return False
        directory = os.path.dirname(os.path.abspath(self.path))
        os.makedirs(directory, exist_ok=True)
        shutil.copyfile(self.seed_path, self.path)
        return True

    def reset(self):
        if not self.restore_seed():
            raise StorageError("Sample data file was not found.")
        self.load()

    def collection(self, name):
        return self.data[name]
