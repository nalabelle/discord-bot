import os

class MissingSecretError(Exception):
    pass

class FileSecrets:
    _instance = None
    paths = [
        "/secrets",
        "/run/secrets",
        "/var/run/secrets",
        ]

    @classmethod
    def Instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, path: str = None):
        if path:
            self.paths = [path]

    def get(self, key: str) -> str:
        secret_file = self.find_file_by_env(key) or self.find_file_in_paths(key)
        if secret_file:
            with open(secret_file, 'r') as file:
                value = file.read().strip()
            return value
        raise MissingSecretError("Could not find secret for {}".format(key))

    def find_file_by_env(self, key: str) -> str:
        lookup = "{}_file".format(key).upper()
        path = os.getenv(lookup)
        return path

    def find_file_in_paths(self, key: str) -> str:
        for path in self.paths:
            if os.path.exists(path):
                secret_file = os.path.join(path, key)
                if os.path.exists(secret_file):
                    return secret_file

