# -*- coding: utf-8 -*-

import os

from storages.neuralstorage import NeuralStorage
from .reinforcement_backend.reinforcementplayer import ReinforcementPlayer
from .reinforcement_backend.training_data import list_training_names, get_meta_info, TRAINING_DATA_DIR

# os.chdir(os.path.join(TRAINING_DATA_DIR, '..'))


def available_training_data():
    return list_training_names()


class ReinforcementDriver(object):
    IS_GUI_CONTROLLED = False

    def __init__(self, meta_name):
        self.config = get_meta_info(meta_name)
        self.store = NeuralStorage(self.config)
        self.player = ReinforcementPlayer(self.store, self.config)

    def configure_new_game(self, player_id, rows, cols, needed_to_win):
        assert rows == self.config['board']['rows']
        assert cols == self.config['board']['cols']
        assert needed_to_win == self.config['needed_to_win']
        self.player_id = player_id
        self.rows = rows
        self.cols = cols
        self.needed_to_win = needed_to_win
        self.exploration = False
        self.previous_action = None
        self.previous_state = None
        
    def learn(self, current_state):
        if self.previous_action and self.previous_state:
            self.player.update_action_value(self.player_id, self.previous_state, self.previous_action, current_state)
            self.player.save_data()

    def make_move(self, board_state):
        if self.exploration:
            selected_action = self.player.select_action_boltzmann(self.player_id, board_state)
        else:
            selected_action = self.player.best_possible_action(self.player_id, board_state)
        self.previous_action = selected_action
        self.previous_state = board_state
        return selected_action
