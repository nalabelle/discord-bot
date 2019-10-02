import os
import json
import logging

class Config(object):
    def __init__(self):
        self.logger = logging.getLogger('Config')
        bot_dir = os.path.dirname(os.path.realpath(__file__))
        self.config_dir = os.path.abspath(os.path.join(bot_dir, '..', 'config'))
        self.config_file = os.path.join(self.config_dir, 'config.json')
        self.create_save_folder()
        self.conf = {}

    def create_save_folder(self):
        if not os.path.exists(self.config_dir):
            self.logger.warn(\
                    'Creating config directory: {}'.format(self.config_dir))
            os.mkdir(self.config_dir)

    def load_config(self):
        self.logger.warn('Loading config... {}'.format(self.config_file))
        if not os.path.isfile(self.config_file):
            self.logger.warn('No config found!')
            return
        state = None
        with open(self.config_file, "r") as f:
            state = json.load(f)
            self.conf = state

    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.conf, f, indent=2, sort_keys=True)

    def set(self, prop, value):
        keys = prop.split('.')
        nesting_level = self.conf
        for nested_key in keys[:-1]:
            nesting_level = nesting_level.setdefault(nested_key, {})
        nesting_level[keys[-1]] = value

    def get(self, prop):
        keys = prop.split('.')
        nesting_level = self.conf
        value = None
        for nested_key in keys:
            value = nesting_level.get(nested_key)
            if value is not None:
                nesting_level = value
            else:
                return None
        return value

config = Config()
config.load_config()

def get(prop):
    return config.get(prop)

def set(prop, value):
    config.set(prop, value)

def save():
    config.save_config()
