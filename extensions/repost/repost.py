from datafile import Data,DataFile
from dataclasses import dataclass, field
from typing import List

@dataclass
class Repost(Data):
    source_channel: str
    dest_channel: str

@dataclass
class RepostData(DataFile):
    subscriptions: List[Repost] = field(default_factory=list)

