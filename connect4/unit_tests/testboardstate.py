import unittest

from common.gamestate import BoardState


class TestBoardState(unittest.TestCase):
    def test_switch_players(self):
        board1 = (BoardState(6, 7)
                  .make_move(1, 1)
                  .make_move(1, 2)
                  .make_move(2, 1)
                  .make_move(3, 2))

        board2 = (BoardState(6, 7)
                  .make_move(1, 2)
                  .make_move(1, 1)
                  .make_move(2, 2)
                  .make_move(3, 1))

        self.assertEqual(board1, board2.switch_players())

    def test_mirror(self):
        board1 = (BoardState(6, 7)
                  .make_move(1, 1)
                  .make_move(1, 2)
                  .make_move(2, 1)
                  .make_move(3, 2))

        board2 = (BoardState(6, 7)
                  .make_move(5, 1)
                  .make_move(5, 2)
                  .make_move(4, 1)
                  .make_move(3, 2))

        self.assertEqual(board1, board2.mirror())


if __name__ == '__main__':
    unittest.main()
