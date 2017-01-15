# -*- coding: utf-8 -*-

import os

from common.helpers import load_yaml_to_dict, save_dict_to_yaml


class ConfigFile:
    def __init__(self, file_path, auto_save=True):
        self.data = {}
        self.file_path = file_path
        self.auto_save = auto_save
        if os.path.exists(file_path):
            self.data = load_yaml_to_dict(file_path)

    def __getitem__(self, name):
        try:
            return self.data[name]
        except KeyError:
            return None

    def __setitem__(self, name, value):
        self.data[name] = value
        if self.auto_save:
            self.save()

    def save(self):
        save_dict_to_yaml(self.data, self.file_path)


config = None


def init_config(file_path):
    global config
    config = ConfigFile(file_path)


def get_config(name, default=None):
    global config
    value = config[name]
    if value is None:
        return default
    else:
        return value


def set_config(name, value):
    global config
    config[name] = value
