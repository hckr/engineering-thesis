# -*- coding: utf-8 -*-


class GuiDriver:
    IS_GUI_CONTROLLED = True

    def configure_new_game(self, player_id, rows, cols, needed_to_win):
        self.player_id = player_id
        self.rows = rows
        self.pointed_col = None

    def bind_gui(self, gui, after_move_callback):
        self.gui = gui
        self.callback = after_move_callback

    def unbind_gui(self):
        self.gui = None
        self.callback = None

    def make_move(self, board_state):
        self.board_state = board_state.board
        self.pointed_col = None
        last_pos_x = self.gui.last_mouse_pos_x()
        if last_pos_x:
            self.on_move(last_pos_x)
        self.gui.bind_events(self.on_move, self.on_click_end)

    def on_move(self, pos_x):
        pointed_col = self.gui.pos_x_to_col(pos_x)
        if pointed_col != self.pointed_col:
            self.pointed_col = pointed_col
            suggestion = None
            for row in range(self.rows - 1, -1, -1):
                if self.board_state[row][pointed_col] is None:
                    suggestion = {
                        'row': row,
                        'col': pointed_col,
                        'player_id': self.player_id
                    }
                    break
            self.gui.refresh_board(suggestion)

    def on_click_end(self, pos_x):
        self.gui.unbind_events()
        self.callback(self.gui.pos_x_to_col(pos_x))
