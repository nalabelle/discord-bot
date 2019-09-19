import random
import os
import json
from random import randrange

class Contest:
    """ Contest library """

    def __init__(self):
        self.prompts = set()
        self.filename = 'drawing_prompts.txt'
        self.shuffled_prompts = []
        self.next_execution = None

    def create_save_folder(self):
        if not os.path.exists('config'):
            os.mkdir('config')

    def set_next_execution(self, next_execution, channel):
        self.next_execution = {
                "time": next_execution,
                "channel": channel
                }

    def save_all_prompts(self):
        state = {
                    "prompts": list(self.prompts),
                    "shuffled": self.shuffled_prompts,
                    "next_execution": self.next_execution
                }
        with open(self.filename, "w") as f:
            json.dump(state, f, indent=2, sort_keys=True)

    def load_prompts(self):
        if not os.path.isfile(self.filename):
            return
        state = None
        with open(self.filename, "r") as f:
            state = json.load(f)
        if state is not None:
            if state.get('next_execution') is not None:
                ne = state['next_execution']
                self.set_next_execution(ne['time'], ne['channel'])
            if len(state['prompts']) > 0:
                self.prompts = set(state['prompts'])
            if len(state['shuffled']) > 0:
                self.shuffled_prompts = state['shuffled']

    def add_prompt(self, prompt):
        prompt = prompt.strip()
        before_length = len(self.prompts)
        self.prompts.add(prompt)
        after_length = len(self.prompts)
        if after_length > before_length:
            index = randrange(len(self.shuffled_prompts)+1)
            self.shuffled_prompts.insert(index, prompt)
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

