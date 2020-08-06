import typing
import yaml
from dataclasses_json import DataClassJsonMixin

A = typing.TypeVar('A', bound="YamlDataclass")
YamlData = typing.Union[str, bytes, bytearray]

class DataClassYamlMixin(DataClassJsonMixin):
    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict())

    @classmethod
    def from_yaml(cls: typing.Type[A], s: YamlData, *, infer_missing=False, **kw) -> A:
        data_dict = yaml.safe_load(s, **kw)
        return cls.from_dict(data_dict, infer_missing=infer_missing)

