from file_secrets.file_secrets import FileSecrets

def secret(key: str) -> str:
    return FileSecrets.Instance().get(key)

