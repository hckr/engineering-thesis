# -*- coding: utf-8 -*-

import os.path
import signal
import sys
from argparse import ArgumentParser, FileType
from datetime import datetime, timedelta

from common.helpers import strip_ext
from storages.neuralstorage import NeuralStorage, STORED_DATA_DIR
from .reinforcementplayer import ReinforcementPlayer
from .training_data import *

arguments_parser = ArgumentParser(
    description='Performs new reinforcement player training based on config file \
                 or resumes previously interrupted training.')
group = arguments_parser.add_mutually_exclusive_group(required=True)
group.add_argument('config_file', nargs='?', type=FileType(), help='path to configuration file')
group.add_argument('-r', '--resume', metavar='TRAINING_NAME', dest='resume_training_name',
                   default=None, help='resume previously interrupted training')
group.add_argument('--delete', nargs='+', metavar='TRAINING_NAME', dest='delete_training_names',
                   default=None, help='remove all data about previous training')
group.add_argument('--delete-all', dest='delete_all', action='store_const', const=True, default=False,
                   help='remove all data about ALL previous trainings')
arguments_parser.add_argument('-l', '--log', dest='log_file', type=FileType(mode='w'), default=None,
                              help="log games played during a training to a file")
if len(sys.argv) == 1:
    arguments_parser.print_help()
    sys.exit(1)
args = arguments_parser.parse_args()
if args.log_file and not (args.config_file or args.resume_training_name):
    arguments_parser.error('log file can be specified only along with config file or previous training name.')


def path_to_store(meta_name):
    return os.path.join(STORED_DATA_DIR, 'reinforcement', meta_name + '.xml')


def delete_meta_file_with_store_data(meta_name):
    try:
        delete_meta_file(meta_name)
    except Exception as e:
        print(e)
    try:
        os.unlink(path_to_store(meta_name))
    except Exception as e:
        print(e)


if args.delete_training_names:
    for training_name in args.delete_training_names:
        delete_meta_file_with_store_data(training_name)
    sys.exit(0)

if args.delete_all:
    for meta_name in list_training_names():
        delete_meta_file_with_store_data(meta_name)
    sys.exit(0)

if args.config_file:
    config = json.load(args.config_file)
    name_prefix = strip_ext(os.path.basename(args.config_file.name))
    meta_name = create_meta_file(name_prefix)
    config['games_played'] = 0
    config['neural_storage']['file_name'] = os.path.relpath(path_to_store(meta_name))
    update_meta_file(meta_name, config)
elif args.resume_training_name and os.path.sep not in args.resume_training_name:
    meta_name = strip_ext(args.resume_training_name)
    config = get_meta_info(meta_name)
    if config is None:
        print('%s.meta not found in %s' % (args.resume_training_name, TRAINING_DATA_DIR))
        sys.exit(1)
else:
    arguments_parser.print_usage()
    sys.exit(1)

print('You can interrupt this process (e.g. with Ctrl+C) and resume later\n'
      'using the following TRAINING_NAME: %s\n' % meta_name)

store = NeuralStorage(config)
player = ReinforcementPlayer(store, config)


def signal_handler(signal, frame):
    print()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

if args.log_file:

    def log_board_state(board_state, id):
        board_state.log(args.log_file, id)

else:

    def log_board_state(board_state, id):
        pass

games_played = config['games_played']
games_to_play = config['games_to_play']
saving_rate = config['saving_rate']
games_per_second = float('nan')
old_time = datetime.now()
should_update_time = False

while games_played < games_to_play:
    games_played += 1
    sys.stdout.write('\rPlaying game %d of %d' % (games_played, games_to_play))
    sys.stdout.flush()
    board_state = player.self_play_game()
    log_board_state(board_state, games_played)
    if games_played % saving_rate == 0:
        player.save_data()
        config['games_played'] = games_played
        update_meta_file(meta_name, config)
        time_delta = datetime.now() - old_time
        time_delta_secs = time_delta.total_seconds()
        games_per_second = saving_rate / time_delta_secs
        print('\n%d games took %s, which is ~%2.2f games/sec. | ETA %s' % (
            saving_rate, str(time_delta), games_per_second,
            str(timedelta(seconds=(games_to_play - games_played) / games_per_second)).rsplit('.', 1)[0]))
        old_time = datetime.now()

player.save_data()

print('\nPlayed %d games. Closing.' % games_played)
