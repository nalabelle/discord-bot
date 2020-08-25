from datafile import Data,DataFile
from dataclasses import dataclass, field
from typing import List

@dataclass
class Repost(Data):
    source_channel: str
    dest_channel: str

    def __eq__(self, other):
        if self.source_channel == other.source_channel:
            if self.dest_channel == other.dest_channel:
                return True
        return False

@dataclass
class RepostData(DataFile):
    subscriptions: List[Repost] = field(default_factory=list)

