import random
import os
from random import randrange
from datetime import datetime, timedelta

class Prompts(object):
    """ Holds Contest prompts """
    def __init__(self, prompts: list=None):
        self.prompts = prompts or list()

    def add_prompt(self, prompt: str, after_index: int=0) -> bool:
        """Inserts the new prompt in a random position after the index given"""
        prompt = prompt.strip()
        if len(self.prompts) == 0:
            self.prompts.append(prompt)
            return True
        if prompt.casefold() not in map(str.casefold, self.prompts):
            index = randrange(after_index+1,len(self.prompts)+1)
            self.prompts.insert(index, prompt)
            return True
        return False

    def remove_prompt(self, prompt: str) -> bool:
        """Removes the given prompt from the prompt list"""
        prompt = prompt.strip()
        if prompt.casefold() in map(string.casefold, self.prompts):
            self.prompts.remove(prompt)
            return True
        return False

    def get_prompt(self, index) -> str:
        if len(self.prompts) > 0 and len(self.prompts) > index:
            return self.prompts[index]
        return None

    def shuffle_prompts(self) -> None:
        random.shuffle(self.prompts)

    def serialize(self) -> str:
        return self.__dict__

    @classmethod
    def deserialize(cls, data):
        if data is None:
            return
        return cls(**data)

class Entry(object):
    """ Represents an entry in a contest """
    def __init__(self, id: str=None, points: int=0, removed: bool=False,
            name: str=None):
        self.id = id
        self.points = points
        self.removed = removed
        self.name = name

    def serialize(self) -> str:
        return self.__dict__

    @classmethod
    def deserialize(cls, data):
        if data is None:
            return
        return cls(**data)


class Contest(object):
    """ Contest for a specific prompt """
    def __init__(self, entries: list=None, contest_end: str=None,
            contest_length: int=None):
        self.entries = entries or list()
        self.contest_end = contest_end
        self.contest_length = contest_length

    @classmethod
    def deserialize(cls, data):
        contest_end = data.get('contest_end')
        contest_length = data.get('contest_length')
        entries = list()
        for entry in data.get('entries'):
            entries.append(Entry.deserialize(entry))
        return cls(entries=entries, contest_end=contest_end,
                contest_length=contest_length)

    def serialize(self) -> str:
        return self.__dict__

    def add_entry(self, entry: Entry) -> bool:
        if entry.id in [x.id for x in self.entries]:
            return False
        self.entries.append(entry)
        return True

    def get_entry(self, entry_id: str) -> dict:
        return self.entries.get(entry_id)

class ContestTracking(object):
    def __init__(self, prompt_index: int=0, prompts: Prompts=None,
            current_contest: Contest=None, previous_contest: Contest=None):
        #start the index at -1 because we increment before delivering the first
        self.prompt_index = prompt_index
        self.prompts = prompts
        self.previous_contest = previous_contest
        self.current_contest = current_contest

    @classmethod
    def deserialize(cls, data):
        prompt_index = data.get('prompt_index')
        prompts = Prompts.deserialize(data.get('prompts'))
        previous_contest = Contest.deserialize(data.get('previous_contest'))
        current_contest = Contest.deserialize(data.get('current_contest'))
        return cls(prompt_index=prompt_index, prompts=prompts,
                previous_contest=previous_contest, current_contest=current_contest)

    def serialize(self) -> str:
        return self.__dict__

    def add_prompt(self, phrase):
        if not self.prompts:
            self.prompts = Prompts()
        return self.prompts.add_prompt(phrase, self.prompt_index)

    def remove_prompt(self, phrase):
        if not self.prompts:
            return False
        return self.prompts.remove_prompt(phrase)

    def shuffle_prompts(self):
        if not self.prompts:
            return False
        self.prompt_index = 0
        return self.prompts.shuffle_prompts()

    def get_current_prompt(self):
        if not self.prompts:
            return None
        #advance the index if we're not currently in a contest
        if not self.current_contest:
            self.prompt_index += 1
        prompt = self.prompts.get_prompt(self.prompt_index)
        return prompt

    def start_contest(self, interval_days: int=None) -> bool:
        if self.current_contest:
            raise Exception('Cannot start contest while one is running')
        if not interval_days and not self.previous_contest:
            raise Exception('Starting contests requires a previous contest '
                    'or a specified length')
        length = interval_days or self.previous_contest.contest_length
        now = datetime.now()
        contest_end = now + timedelta(days=length)
        prompt = self.get_current_prompt()
        if prompt:
            self.current_contest = Contest(contest_end=contest_end.isoformat(' '),
                    contest_length=length)
            return True
        return False

    def get_contest_end(self):
        if not self.current_contest:
            return None
        return datetime.strptime(self.current_contest.contest_end, "%Y-%m-%d %H:%M:%S.%f")

    def stop_contest(self) -> bool:
        if not self.current_contest:
            return False
        self.previous_contest = self.current_contest
        self.current_contest = None
        return True

    def add_entry(self, entry_id: str, user_id: str, points: int=0) -> bool:
        if not self.current_contest:
            return False
        if not entry_id or not user_id:
            return False
        entry = Entry(id=entry_id,name=user_id,points=points)
        return self.current_contest.add_entry(entry)

    def get_entry(self, entry_id: str) -> dict:
        if not self.current_contest:
            return None
        if not entry_id:
            return None
        return self.current_contest.get_entry(entry_id)

