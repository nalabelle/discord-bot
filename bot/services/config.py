import os
import yaml
import json
import logging
from collections.abc import MutableMapping

log = logging.getLogger('Config')

class Config(MutableMapping):
    def __init__(self, path=None, allow_env=False):
        self.config_file = path
        self.create_save_folder()
        self.mapping = self.load_config()
        self.secrets_path = self.get('secrets_path', '/var/run/secrets')
        self.use_env = allow_env

    def load_config(self):
        log.info('Loading config... {}'.format(self.config_file))
        config = {}
        if not os.path.isfile(self.config_file):
            log.warn('No config found!')
        else:
            with open(self.config_file, "r") as f:
                config = yaml.safe_load(f)
        return config

    def save_config(self):
        # these dumpers like to write empty files when they crash
        conf_string = yaml.safe_dump(self.mapping)
        with open(self.config_file, "w") as f:
            f.write(conf_string)

    def dump(self):
        return yaml.dump(self.mapping)

    def __getitem__(self, key, other=None, check_file=False):
        return self.get(**args)

    def get(self, key, default=None, check_file=False):
        value = self.mapping.get(key, default)
        if not default and not value and check_file:
            path = os.path.join(self.secrets_path, key)
            with open(path, 'r') as file:
                value = file.read().strip()
        return value

    def __setitem__(self, key, value):
        return self.get(**args)

    def set(self, prop, value):
        self.mapping[prop] = value

    def __delitem__(self):
        '''
         Your Implementation for deleting the Item goes here
        '''
        raise NotImplementedError("del needs to be implemented")
    def __iter__(self):
        '''
         Your Implementation for iterating the dictionary goes here
        '''
        raise NotImplementedError("Iterating the collection needs to be implemented")
    def __len__(self):
        '''
         Your Implementation for determing the size goes here
        '''
        raise NotImplementedError("len(obj) determination needs to be implemented")

    def create_save_folder(self):
        if not self.config_file:
            return
        path = os.path.dirname(self.config_file)
        if not os.path.exists(path):
            log.info(\
                    'Creating config directory: {}'.format(path))
            os.mkdir(path)

#    def set(self, prop, value):
#        keys = prop.split('.')
#        nesting_level = self.conf
#        for nested_key in keys[:-1]:
#            nesting_level = nesting_level.setdefault(nested_key, {})
#        nesting_level[keys[-1]] = value
#
#    def get(self, prop, default=None, check_file=False):
#        value = self.conf.get(prop, default)
#        #nesting_level = self.conf
#        #keys = prop.split('.')
#        #for nested_key in keys:
#        #    value = nesting_level.get(nested_key)
#        #    if value is not None:
#        #        nesting_level = value
#        #    else:
#        #        return None
#        return value

