# -*- coding: utf-8 -*-

from random import randint


class RandomDriver(object):
    IS_GUI_CONTROLLED = False

    def configure_new_game(self, player_id, rows, cols, needed_to_win):
        self.cols = cols

    def make_move(self, board_state):
        while True:
            column = randint(0, self.cols - 1)
            if board_state.board[0][column] is None:
                break
        return column
