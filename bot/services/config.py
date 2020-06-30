import logging
import os
import yaml

from abc import ABCMeta
from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin, Exclude, config
from typing import List, TypeVar, Type, Dict

log = logging.getLogger('Config')
A = TypeVar('A', bound="YamlDataclass")

@dataclass
class YamlDataClass(DataClassJsonMixin, metaclass=ABCMeta):
    __file_path__: str = field(default=None, init=False,
            metadata=config(exclude=Exclude.ALWAYS))

    def __path__(self):
        if self.__file_path__ is not None:
            return self.__file_path__
        config = Config()
        cls_name = self.__class__.__name__
        path = os.path.join(config.data_path, "{}.yml".format(cls_name.replace('Data','').lower()))
        self.__file_path__ = path
        return path

    def create_save_folder(self, path: str) -> None:
        dir_path = os.path.dirname(path)
        if os.path.exists(dir_path):
            return
        log.info(\
                'Creating data directory: {}'.format(dir_path))
        os.mkdir(dir_path)

    def load(self, path: str = None) -> bool:
        if not path:
            path = self.__path__()
        if os.path.exists(path):
            with open(path, "r", encoding="UTF-8") as f:
                data_dict = yaml.safe_load(f)
            self.__dict__.update(self.__class__.schema().load(data_dict).__dict__)
            return True
        return False

    @classmethod
    def from_yaml(cls: Type[A], path: str, infer_missing=False) -> A:
        with open(path, "r", encoding="UTF-8") as f:
            data_dict = yaml.safe_load(f)
        return cls.from_dict(data_dict, infer_missing=infer_missing)


    def save(self, path: str = None) -> bool:
        if not path:
            path = self.__path__()
        # these dumpers like to write empty files when they crash
        self.create_save_folder(path)
        conf_string = yaml.safe_dump(self.to_dict())
        with open(path, "w", encoding="UTF-8") as f:
            f.write(conf_string)
        return True

    def dump(self) -> str:
        return yaml.dump(self.to_dict())

class Data(YamlDataClass):
    pass

@dataclass
class BotConfig(YamlDataClass):
    command_prefix: str = os.getenv('COMMAND_PREFIX', '!')
    extensions: List[str] = field(default_factory=list)
    log_level: str = os.getenv('LOG_LEVEL', 'ERROR')
    data_path: str = os.getenv('DATA_PATH') or \
        os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data'))
    secrets: Dict[str, str] = field(default_factory=dict)

class ConfigSingleton:
    config_instance = None
    secrets_instance = None

def Config():
    if ConfigSingleton.config_instance is None:
        ConfigSingleton.config_instance = BotConfig()
    return ConfigSingleton.config_instance

class BotSecrets:
    class MissingSecretError(Exception):
        pass

    def get(self, key):
        value = os.getenv(key.upper())
        if value:
            return value
        config = Config()
        lookup = "{}_file".format(key.lower())
        path = os.getenv(lookup.upper()) or config.secrets.get(lookup)
        if path:
            with open(path, 'r') as file:
                value = file.read().strip()
            return value
        raise self.MissingSecretError("Could not find secret for {}".format(key))

def Secrets(secret_key: str = None):
    if ConfigSingleton.secrets_instance is None:
        ConfigSingleton.secrets_instance = BotSecrets()
    if secret_key:
        return ConfigSingleton.secrets_instance.get(secret_key)
    else:
        return ConfigSingleton.secrets_instance

