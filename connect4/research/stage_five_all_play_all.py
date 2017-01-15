# -*- coding: utf-8 -*-

import signal
import sys

from game_agents.duel import get_available_drivers
from .stage import all_play_all


def signal_handler(signal, frame):
    print()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

drivers_to_duel = filter(lambda x: x.startswith('reinforcement-stage_five_'), get_available_drivers())

all_play_all(drivers_to_duel)
