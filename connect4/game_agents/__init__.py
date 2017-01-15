# -*- coding: utf-8 -*-

import os

THIS_DIR = os.path.dirname(os.path.realpath(__file__)).split(os.sep)[-1]


def new_driver_object(algorithm, driver_name, *args, **kwargs):
    module = __import__('%s.%s' % (THIS_DIR, algorithm), fromlist=[algorithm])
    klass = getattr(module, '%sDriver' % algorithm.capitalize())
    driver = klass(*args, **kwargs)
    setattr(driver, 'DRIVER_NAME', driver_name)
    return driver
