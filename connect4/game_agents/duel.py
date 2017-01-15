# -*- coding: utf-8 -*-

import signal
import sys
from argparse import ArgumentParser, FileType

from common.gamestate import GameState
from common.helpers import natural_key
from . import new_driver_object
from .reinforcement import available_training_data

rows = 6
cols = 7
needed_to_win = 4

available_drivers = {
    'random': ['random', 'Computer (random)']
}

for config_name in available_training_data():
    driver_id = 'reinforcement-%s' % config_name
    available_drivers[driver_id] = ['reinforcement', 'Computer (%s)' % config_name, config_name]


def get_available_drivers():
    return sorted(available_drivers.keys(), key=natural_key)


def duel(player1_driver, player2_driver, games_to_play, log_file=None):
    scoreboard = {
        1: 0,
        2: 0,
        'draws': 0
    }

    player1 = new_driver_object(*available_drivers[player1_driver])
    player2 = new_driver_object(*available_drivers[player2_driver])
    game_state = GameState(rows, cols, needed_to_win)

    for i in range(1, games_to_play + 1):
        game_state.start_new_game(player1, player2)
        while True:
            column = game_state.get_current_player().make_move(game_state.board_state)
            game_state.save_move(column)
            result = game_state.game_result()
            if result:
                if result['result'] == 'won':
                    scoreboard[result['player_id']] += 1
                else:
                    scoreboard['draws'] += 1
                break
            game_state.next_player()
        if log_file:
            game_state.board_state.log(log_file, i)

    return scoreboard


def main():
    arguments_parser = ArgumentParser(
        description='Blah, blah...')
    arguments_parser.add_argument('player1_driver', nargs='?', help="name of the first player's driver")
    arguments_parser.add_argument('player2_driver', nargs='?', help="name of the second player's driver")
    arguments_parser.add_argument('games_to_play', nargs='?', type=int, help="number of games to play")
    arguments_parser.add_argument('-d', '--list-drivers', dest='list_drivers', action='store_const',
                                  const=True, default=False, help="list all available drivers")
    arguments_parser.add_argument('-l', '--log', dest='log_file', type=FileType(mode='w'), default=None,
                                  help="log games played during a duel to a file")
    if len(sys.argv) == 1:
        arguments_parser.print_help()
        sys.exit(1)
    args = arguments_parser.parse_args()

    if args.list_drivers:
        print('\n'.join(get_available_drivers()))
        sys.exit(0)

    if args.player1_driver is None:
        arguments_parser.error('player1_driver not specified')

    if args.player2_driver is None:
        arguments_parser.error('player2_driver not specified')

    if args.games_to_play is None:
        arguments_parser.error('games_to_play not specified')

    for name in (args.player1_driver, args.player2_driver):
        if name not in available_drivers:
            arguments_parser.error('%s is not a name of an existing driver' % name)

    def signal_handler(signal, frame):
        print()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    scoreboard = duel(args.player1_driver, args.player2_driver, args.games_to_play, args.log_file)

    print('%d %d %d' % (scoreboard[1], scoreboard['draws'], scoreboard[2]))
