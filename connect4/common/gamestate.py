# -*- coding: utf-8 -*-

from copy import deepcopy
from datetime import datetime


class BoardState:
    def __init__(self, rows=None, cols=None,
                 board=None, free_fields=None):
        self.rows = rows
        self.cols = cols
        if None not in [board, free_fields]:
            self.board = board
            self.free_fields = free_fields
        else:
            self.board = [[None] * self.cols for _ in range(self.rows)]
            self.free_fields = rows * cols

    def __str__(self):
        return str(self.board)

    def __eq__(self, other):
        return self.board == other.board

    def make_move(self, column, player_id):
        new_board = deepcopy(self.board)
        row = self.get_available_row_in_col(column)
        if row is None or new_board[row][column] is not None:
            raise ValueError('This field has already been occupied.')
        new_board[row][column] = player_id
        return BoardState(
            rows=self.rows,
            cols=self.cols,
            board=new_board,
            free_fields=self.free_fields - 1
        )

    def get_available_row_in_col(self, col):
        for row in range(self.rows - 1, -1, -1):
            if self.board[row][col] is None:
                return row
        return None

    def switch_players(self):
        new_board = []
        for row in self.board:
            new_row = []
            for field in row:
                if field is None:
                    new_row.append(None)
                elif field == 1:
                    new_row.append(2)
                elif field == 2:
                    new_row.append(1)
            new_board.append(new_row)
        return BoardState(
            rows=self.rows,
            cols=self.cols,
            board=new_board,
            free_fields=self.free_fields
        )

    def mirror(self):
        new_board = []
        for row in self.board:
            new_board.append(list(reversed(row)))
        return BoardState(
            rows=self.rows,
            cols=self.cols,
            board=new_board,
            free_fields=self.free_fields
        )

    def game_result(self, needed_to_win):
        for player_id in (1, 2):
            won_result = {
                'result': 'won',
                'player_id': player_id
            }

            # check rows:
            for row in range(self.rows):
                chain_length = 0
                for col in range(self.cols):
                    if self.board[row][col] == player_id:
                        chain_length += 1
                        if chain_length == needed_to_win:
                            return won_result
                    else:
                        chain_length = 0
                chain_length = 0

            # check columns:
            for col in range(self.cols):
                chain_length = 0
                for row in range(self.rows):
                    if self.board[row][col] == player_id:
                        chain_length += 1
                        if chain_length == needed_to_win:
                            return won_result
                    else:
                        chain_length = 0
                chain_length = 0

            # check diagonals:
            for row in range(self.rows):
                for col in range(self.cols):
                    if self.board[row][col] == player_id:
                        # check NW-SE diagonal:
                        chain_length = 1
                        for i in range(1, needed_to_win):
                            r = row + i
                            if r >= self.rows:
                                break
                            c = col + i
                            if c >= self.cols:
                                break
                            if self.board[r][c] == player_id:
                                chain_length += 1
                                if chain_length == needed_to_win:
                                    return won_result
                            else:
                                break
                        # check NE-SW diagonal:
                        chain_length = 1
                        for i in range(1, needed_to_win):
                            r = row + i
                            if r >= self.rows:
                                break
                            c = col - i
                            if c < 0:
                                break
                            if self.board[r][c] == player_id:
                                chain_length += 1
                                if chain_length == needed_to_win:
                                    return won_result
                            else:
                                break

            if self.free_fields == 0:
                return {
                    'result': 'tied'
                }

        return None  # there is no result yet

    def log(self, stream, id):
        stream.write('Game %d | ' % id)
        stream.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        stream.write('\n  ')
        for col_id in range(self.cols):
            stream.write('%d ' % col_id)
        stream.write('\n')
        for row_id, row in enumerate(self.board):
            stream.write('%d ' % row_id)
            for x in row:
                if x == 1:
                    stream.write('+ ')
                elif x == 2:
                    stream.write('= ')
                else:
                    stream.write('  ')
            stream.write('\n')
        stream.write('\n\n')
        stream.flush()


class GameState(object):
    def __init__(self, rows, cols, needed_to_win):
        self.rows = rows
        self.cols = cols
        self.needed_to_win = needed_to_win
        self.players = {}

    def start_new_game(self, player1, player2):
        self.board_state = BoardState(self.rows, self.cols)
        player1.configure_new_game(1, self.rows, self.cols, self.needed_to_win)
        player2.configure_new_game(2, self.rows, self.cols, self.needed_to_win)
        self.players[1] = player1
        self.players[2] = player2
        self.current_player_id = 1

    def save_move(self, column):
        self.board_state = self.board_state.make_move(column, self.current_player_id)

    def next_player(self):
        self.current_player_id = 1 if self.current_player_id == 2 else 2

    def get_current_player(self):
        return self.players[self.current_player_id]

    def get_available_move_in_col(self, col):
        row = self.board_state.get_available_row_in_col(col)
        if row is not None:
            return {
                'row': row,
                'col': col
            }
        return None

    def game_result(self):
        return self.board_state.game_result(self.needed_to_win)
