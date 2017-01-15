# -*- coding: utf-8 -*-

import os
from glob import iglob

from PIL import Image, ImageTk


def import_images(glob_path, new_size=None, increase_alpha_by=0):
    images = {}
    for file_name in iglob(glob_path):
        name_without_extension = os.path.basename(file_name).split('.')[0]
        images[name_without_extension] = import_image(file_name, new_size, increase_alpha_by)
    return images


def import_image(file_name, new_size=None, increase_transparency_by=0):
    image = Image.open(file_name).convert('RGBA')
    if increase_transparency_by != 0:
        decrease = decreaser_with_limit(increase_transparency_by, 0)
        image.putdata([(r, g, b, decrease(a)) for r, g, b, a in image.getdata()])
    if type(new_size) in (tuple, list):
        return ImageTk.PhotoImage(image.resize(new_size, Image.ANTIALIAS))
    if type(new_size) is int:
        return ImageTk.PhotoImage(image.resize((new_size, new_size), Image.ANTIALIAS))
    if new_size is None:
        return ImageTk.PhotoImage(image)
    raise AttributeError('Wrong value for new_size')


def decreaser_with_limit(amount, min_val):
    def decreaser(value):
        new_value = value - amount
        if new_value < min_val:
            return 0
        else:
            return new_value

    return decreaser
