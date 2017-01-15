# -*- coding: utf-8 -*-

import re
import yaml


def load_yaml_to_dict(file_path):
    return yaml.safe_load(open(file_path, encoding='utf-8'))


def save_dict_to_yaml(dictionary, file_path):
    yaml.dump(dictionary, open(file_path, 'w'), default_flow_style=False, encoding='utf-8')


def strip_ext(file_name):
    return re.sub(r'\.[^\.]*$', '', file_name)


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_key(text):
    return [atoi(c) for c in re.split('(\d+)', text)]
