# -*- coding: utf-8 -*-

from __future__ import division

import random
from operator import itemgetter

import numpy as np

from common.gamestate import BoardState


def other_player(player_id):
    if player_id == 1:
        return 2
    elif player_id == 2:
        return 1


def state_transition(player_id, state, action):
    return state.make_move(action, player_id)


class ReinforcementPlayer:
    def __init__(self, data_storage, config):
        assert data_storage.rows == config['board']['rows']
        assert data_storage.cols == config['board']['cols']
        assert config['estimated_optimal_future_value'] in ('best_known', 'mean')
        self.data_storage = data_storage
        self.config = config
        if config['estimated_optimal_future_value'] == 'best_known':
            self.estimated_optimal_future_value = self.estimated_optimal_future_value_best_known
        elif config['estimated_optimal_future_value'] == 'mean':
            self.estimated_optimal_future_value = self.estimated_optimal_future_value_mean
        self.boltzmann_temperature = self.config['boltzmann_temperature']

    def is_terminal(self, state):
        return state.game_result(self.config['needed_to_win']) is not None

    def get_possible_actions(self, state):
        return [col for col in range(self.config['board']['cols'])
                if state.get_available_row_in_col(col) is not None]

    def reward_in_state(self, player_id, state):
        game_result = state.game_result(self.config['needed_to_win'])
        if game_result is None:
            return self.config['rewards']['each_move']
        else:
            if game_result['result'] == 'won':
                if game_result['player_id'] == player_id:
                    return self.config['rewards']['win']
                else:
                    return self.config['rewards']['loss']
            elif game_result['result'] == 'tied':
                return self.config['rewards']['tie']

    def best_possible_action_with_value(self, player_id, state):
        possible_actions = self.get_possible_actions(state)
        actions_with_values = [(action, self.data_storage.get_value_of_action(player_id, state, action))
                               for action in possible_actions]
        best_action_with_value = sorted(actions_with_values, key=itemgetter(1), reverse=True)[0]
        return best_action_with_value

    def best_possible_action(self, player_id, state):
        return self.best_possible_action_with_value(player_id, state)[0]

    def random_possible_action(self, state):
        possible_actions = self.get_possible_actions(state)
        return random.choice(possible_actions)

    def select_action_boltzmann(self, player_id, state):
        possible_actions = self.get_possible_actions(state)
        actions_with_values = [(action, self.data_storage.get_value_of_action(player_id, state, action))
                               for action in possible_actions]
        actions, values = zip(*actions_with_values)
        numerators = np.exp(np.array(values) / self.boltzmann_temperature)
        denumerator = sum(numerators)
        probabilities = numerators / denumerator
        return np.random.choice(actions, p=probabilities)

    def estimated_optimal_future_value_mean(self, player_id, state):
        possible_actions = self.get_possible_actions(state)
        if len(possible_actions) == 0:
            return 0
        rewards = 0
        for action in possible_actions:
            possible_state = state.make_move(action, other_player(player_id))
            if not self.is_terminal(possible_state):
                best_next_action = self.best_possible_action(player_id, possible_state)
                rewards += self.data_storage.get_value_of_action(player_id, possible_state, best_next_action)
        return rewards / len(possible_actions)

    def estimated_optimal_future_value_best_known(self, player_id, state):
        if not self.is_terminal(state):
            best_opponents_action = self.best_possible_action(other_player(player_id), state)
            worst_possible_state = state.make_move(best_opponents_action, other_player(player_id))
            if not self.is_terminal(worst_possible_state):
                _, best_next_action_value = self.best_possible_action_with_value(player_id, worst_possible_state)
                return best_next_action_value
        return 0

    def best_next_state(self, player_id, state):
        action = self.best_possible_action(player_id, state)
        return state_transition(player_id, state, action)

    def update_action_value(self, player_id, old_state, action, new_state):
        reward = self.reward_in_state(player_id, new_state)
        learned_value = reward + self.config['discount_factor'] * self.estimated_optimal_future_value(player_id, new_state)
        self.data_storage.update_value_of_action(player_id, old_state, action, learned_value)

    def self_play_game(self):
        board_state = BoardState(self.config['board']['rows'], self.config['board']['cols'])
        while True:
            for player_id in (1, 2):
                selected_action = self.select_action_boltzmann(player_id, board_state)
                new_state = board_state.make_move(selected_action, player_id)
                self.update_action_value(player_id, board_state, selected_action, new_state)
                board_state = new_state
                if self.is_terminal(board_state):
                    return board_state

    def save_data(self):
        self.data_storage.save()
