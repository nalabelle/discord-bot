import os
import typing
from dataclasses_yaml import DataClassYamlMixin

DataFile = typing.TypeVar('DataFile', bound="DataFile")

class Data(DataClassYamlMixin):
    pass
#    def __post_init__(self):
#        if not self.path:
#            name = self.__class__.__name__.replace('Data','').lower()
#            config = Config()
#            self.path = os.path.join(config.data_path, "{}.yml".format(name))
#            if os.path.exists(self.path):
#                self.__dict__.update(self.__class__.from_yaml(path=self.path).__dict__)

class DataFile(Data):
    @classmethod
    def from_yaml(cls: typing.Type[DataFile], path: str, *, infer_missing=False, **kw) -> DataFile:
        if os.path.exists(path):
            with open(path, "r", encoding="UTF-8") as f:
                df = super().from_yaml(f, infer_missing=infer_missing, **kw)
                df.path = path
                return df
        else:
            datafile = cls()
            datafile.path = path
            datafile.save()
            return datafile

    def save(self) -> None:
        save_dir = os.path.dirname(self.path)
        if save_dir and save_dir != '':
            if not os.path.exists(save_dir):
                os.mkdir(save_dir)
        conf_string = self.to_yaml()
        with open(self.path, "w", encoding="UTF-8") as f:
            f.write(conf_string)

    def dump(self) -> str:
        return self.to_yaml()

