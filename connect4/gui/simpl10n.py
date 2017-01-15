# -*- coding: utf-8 -*-

import os
from glob import iglob

from common.helpers import load_yaml_to_dict

L10N_DIR = os.path.join(os.path.dirname(__file__), 'l10n_files')


def get_available_langs():
    result = {}
    for file_name in iglob(os.path.join(L10N_DIR, '*.yaml')):
        lang_code = os.path.basename(file_name).split('.')[0]
        result[lang_code] = load_yaml_to_dict(file_name)['__langname']
    return result


AVAILABLE_LANGS = get_available_langs()
FALLBACK_LANG = 'en'

dictionary = {}
current_language = None
fallback_dictionary = {}


def set_language(lang_code, fallback=FALLBACK_LANG):
    global dictionary, fallback_dictionary
    dictionary, fallback_dictionary = {}, {}
    langs_to_dicts = [(lang_code, dictionary)]
    if lang_code != fallback:
        langs_to_dicts.append((fallback, fallback_dictionary))
    for lang, lang_dict in langs_to_dicts:
        file_path = os.path.join(L10N_DIR, lang + '.yaml')
        if os.path.exists(file_path):
            lang_dict.update(load_yaml_to_dict(file_path))
        else:
            raise IOError('No file for language ' + lang + ' found.')
    global current_language
    current_language = lang_code


def translate(phrase, format_vals={}):
    global dictionary, fallback_dictionary
    ans = phrase
    for d in (dictionary, fallback_dictionary):
        translation = d.get(phrase, None)
        if translation is not None:
            ans = translation
            break
    return ans % format_vals


def get_current_lang():
    global current_language
    return current_language
