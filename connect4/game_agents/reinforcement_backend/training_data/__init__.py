# -*- coding: utf-8 -*-

import json
import os.path
from glob import glob

from common.helpers import strip_ext, natural_key

TRAINING_DATA_DIR = os.path.dirname(__file__)


def list_training_names():
    return sorted([strip_ext(os.path.basename(x)) for x in glob(os.path.join(TRAINING_DATA_DIR, '*.meta'))],
                  key=natural_key)


def get_meta_info(name):
    path = os.path.join(TRAINING_DATA_DIR, name + '.meta')
    if os.path.isfile(path):
        with open(path) as file:
            return json.load(file)
    return None


def create_meta_file(name_prefix):
    i = 1
    while True:
        name = '%s-%i' % (name_prefix, i)
        file_name = name + '.meta'
        path = os.path.join(TRAINING_DATA_DIR, file_name)
        if not os.path.isfile(path):
            open(path, 'w').close()
            return name
        i += 1


def delete_meta_file(meta_name):
    path = os.path.join(TRAINING_DATA_DIR, meta_name + '.meta')
    os.unlink(path)


def update_meta_file(name, config):
    file_name = name + '.meta'
    path = os.path.join(TRAINING_DATA_DIR, file_name)
    if os.path.isfile(path):
        with open(path, 'w') as file:
            json.dump(config, file, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        raise Exception('That meta file does not exist yet!')
