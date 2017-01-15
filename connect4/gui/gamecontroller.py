# -*- coding: utf-8 -*-
from copy import deepcopy

from common.gamestate import GameState
from .configfile import set_config
from .gamegui import GameGUI
from . import simpl10n as l10n
from .simpl10n import translate as _


class GameController:
    def __init__(self, title, rows, cols, needed_to_win, chip_size, game_agents):
        self.game_state = GameState(rows, cols, needed_to_win)
        self.game_gui = GameGUI(self, title, rows, cols, chip_size)
        self.game_agents = game_agents

    def start_gui(self):
        self.game_gui.start()

    @staticmethod
    def get_current_lang():
        return l10n.get_current_lang()

    def get_rows_count(self):
        return self.game_state.rows

    def get_cols_count(self):
        return self.game_state.cols

    def get_board_state(self):
        try:
            return self.game_state.board_state
        except AttributeError:
            return None

    @staticmethod
    def set_lang(lang):
        set_config('lang', lang)
        l10n.set_language(lang)

    def set_lang_and_restart_gui(self, lang):
        self.set_lang(lang)
        self.game_gui.restart()

    def set_chip_size_and_restart_gui(self, chip_size):
        set_config('chip_size', chip_size)
        self.game_gui.chip_size = chip_size
        self.game_gui.restart()

    def on_new_game(self, *args):
        labels = [_(x.DRIVER_NAME) for x in self.game_agents]

        def cb(p1_index, p2_index):
            player1_object = self.game_agents[p1_index]
            player2_object = self.game_agents[p2_index]
            if id(player1_object) == id(player2_object):
                player1_object.unbind_gui() # to avoid infinite recursion
                player2_object = deepcopy(player1_object)
            self.start_new_game(player1_object, player2_object)

        self.game_gui.select_players(labels, cb)

    def is_player_gui_controlled(self, player_id):
        return self.game_state.players[player_id].IS_GUI_CONTROLLED

    def start_new_game(self, player1_object, player2_object):
        for index, player in enumerate([player1_object, player2_object]):
            player.configure_new_game(index + 1, self.game_state.rows, self.game_state.cols,
                                      self.game_state.needed_to_win)
            if player.IS_GUI_CONTROLLED:
                player.bind_gui(self.game_gui, self.after_move)
        self.game_state.start_new_game(player1_object, player2_object)
        self.game_gui.refresh_board()
        self.before_move()

    def before_move(self):
        player = self.game_state.get_current_player()
        board_state = self.game_state.board_state
        if self.is_player_gui_controlled(self.game_state.current_player_id):
            player.make_move(board_state)
        else:
            self.after_move(player.make_move(board_state))

    def after_move(self, selected_col):
        player = self.game_state.get_current_player()
        avail_move = self.game_state.get_available_move_in_col(selected_col)
        if avail_move is None:
            if player.IS_GUI_CONTROLLED:
                self.before_move()
                return
            else:
                raise ValueError('Player driver %s made illegal move.' % player.__class__.__name__)
        self.game_state.save_move(avail_move['col'])
        self.game_gui.refresh_board()
        game_result = self.game_state.game_result()
        if game_result is not None:
            if game_result['result'] == 'won':
                self.game_gui.show_info(_(u'Game over'), _('Player %d won!', game_result['player_id']))
                return
            if game_result['result'] == 'tied':
                self.game_gui.show_info(_(u'Game over'), _('It\'s tied!'))
                return
            raise Exception('Should not be here.')
        else:
            self.game_state.next_player()
            self.before_move()
