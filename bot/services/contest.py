import random
import os
from random import randrange
import services.config

class Contest:
    """ Contest library """

    def __init__(self):
        self.prompts = set()
        self.shuffled_prompts = []
        self.next_execution = None
        self.load_from_config()

    def load_from_config(self):
        self.next_execution = services.config.get('contest.next_execution')
        if self.next_execution is not None:
            self.set_next_execution(
                    self.next_execution['time'], \
                    self.next_execution['channel'],\
                    self.next_execution['days'])
        prompts = services.config.get('contest.prompts')
        if prompts is not None:
            self.prompts = set(prompts)
        shuffled = services.config.get('contest.shuffled')
        if shuffled is not None:
            self.shuffled_prompts = shuffled

    def save_to_config(self):
        services.config.set('contest.next_execution', self.next_execution)
        services.config.set('contest.prompts', list(self.prompts))
        services.config.set('contest.shuffled', self.shuffled_prompts)
        services.config.save()

    def set_next_execution(self, next_execution=None, channel=None, days=1):
        if channel is None or next_execution is None:
            self.next_execution = None
            return
        self.next_execution = {
                "time": next_execution,
                "channel": channel,
                "days": days
                }
        self.save_to_config()

    def add_prompt(self, prompt):
        prompt = prompt.strip()
        before_length = len(self.prompts)
        self.prompts.add(prompt)
        after_length = len(self.prompts)
        if after_length > before_length:
            index = randrange(len(self.shuffled_prompts)+1)
            self.shuffled_prompts.insert(index, prompt)
            self.save_to_config()
            return True
        return False

    def dump_prompts(self):
        return self.prompts

    def dump_shuffled_prompts(self):
        return self.shuffled_prompts

    def get_prompt(self):
        if len(self.shuffled_prompts) > 0:
            return self.shuffled_prompts.pop(0)

    def shuffle_prompts(self):
        prompt_list = list(self.prompts)
        random.shuffle(prompt_list)
        self.shuffled_prompts = prompt_list
        self.save_to_config()

