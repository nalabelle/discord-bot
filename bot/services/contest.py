import random
from random import randrange

class Contest:
    """ Contest library """

    def __init__(self):
        self.prompts = set()
        self.shuffled_prompts = []

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
        return self.shuffled_prompts.pop(0)

    def shuffle_prompts(self):
        prompt_list = list(self.prompts)
        random.shuffle(prompt_list)
        self.shuffled_prompts = prompt_list

