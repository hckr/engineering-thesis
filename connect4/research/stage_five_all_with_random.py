# -*- coding: utf-8 -*-

import signal
import sys

from game_agents.duel import get_available_drivers
from .stage import all_with_random


def signal_handler(signal, frame):
    print()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

drivers_to_duel = filter(lambda x: x.startswith('reinforcement-stage_five_'), get_available_drivers())

GAMES_PER_DUEL = 1000

all_with_random(drivers_to_duel, GAMES_PER_DUEL)
