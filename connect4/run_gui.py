#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path

from gui.simpl10n import FALLBACK_LANG
from gui import simpl10n as l10n
from gui.gamegui import DEFAULT_CHIP_SIZE
from gui.simpl10n import translate as _
from gui.configfile import init_config, get_config
from gui.gamecontroller import GameController
from game_agents import new_driver_object
from game_agents.reinforcement import available_training_data

init_config(os.path.join(os.path.dirname(__file__), 'gui', 'config.yaml'))
l10n.set_language(get_config('lang', FALLBACK_LANG))


def should_be_visible(training_name):
    return training_name.startswith('stage_six_6') or \
           training_name.startswith('stage_six_1')


agents = [
    new_driver_object('gui', 'Human'),
    new_driver_object('random', 'Computer (random)')
]

for config_name in filter(should_be_visible, available_training_data()):
    agents.append(new_driver_object('reinforcement', _('Computer (%s)', config_name), config_name))

game_controller = GameController(
    title='Connect 4',
    rows=6,
    cols=7,
    needed_to_win=4,
    chip_size=get_config('chip_size', DEFAULT_CHIP_SIZE),
    game_agents=agents
)
game_controller.start_gui()
