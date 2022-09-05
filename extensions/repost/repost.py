from __future__ import annotations

import logging
from pathlib import Path
from typing import NewType

from pydantic import Field
from pydantic_yaml import YamlModel

DATAFILE = "repost.yaml"

log = logging.getLogger("Repost")

SourceChannel = NewType("SourceChannel", int)
LinkedChannel = NewType("LinkedChannel", int)


class RepostData(YamlModel):
    path: Path = Field(None, alias="_path", exclude=True, allow_mutation=True)
    subscriptions: dict[SourceChannel, set[LinkedChannel]] = {}

    def linked_channels(self, source: SourceChannel) -> list[LinkedChannel]:
        subs = self.subscriptions.get(source, [])
        return subs

    def add_link(self, source: SourceChannel, link: LinkedChannel) -> bool:
        """Stores a channel with a source"""
        links = self.subscriptions.setdefault(source, set())
        if link in links:
            return False
        links.add(link)
        self.save()
        return True

    def remove_link(self, source: SourceChannel, link: LinkedChannel) -> bool:
        """Removes a linked channel from a source"""
        links = self.subscriptions.setdefault(source, set())
        if link not in links:
            return False
        links.remove(link)
        self.save()
        return True

    def set_path(self, path: Path) -> None:
        self.path = path

    def save(self) -> None:
        with self.path.open("w", encoding="utf-8") as file:
            file.write(self.yaml())

    @staticmethod
    def from_yaml(path: Path) -> RepostData:
        obj = None
        if path.exists():
            obj = RepostData.parse_file(str(path))
        if not obj:
            obj = RepostData()
        obj.set_path(path)
        return obj

    class Config:
        fields = {"_path": {"exclude": True}}
        underscore_attrs_are_private = False
