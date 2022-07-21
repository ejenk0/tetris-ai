from copy import deepcopy
from typing import Sequence
from main import Board, NextPieceDisplay, ScoreDisplay
import pygame as pg


class TetrisClientV1:
    def __init__(self, board: Board):
        self.board = board

    def update(self, tick: bool = False):
        self.board.update(tick=tick)

    def draw(self, surf: pg.surface.Surface):
        pg.sprite.GroupSingle(self.board).draw(surf)

    def move(self):
        self.board.input(self.calculate_move())

    def calculate_move(self) -> Sequence[str]:
        perms = self.find_permutations(self.board)
        if perms:
            ## APPROACH 1

            # min_holes = min(perms, key=lambda x: x["board"].count_holes())[
            #     "board"
            # ].count_holes()
            # lowest_holes = [x for x in perms if x["board"].count_holes() == min_holes]

            # # Get lowest height perms
            # min_height = min(lowest_holes, key=lambda x: x["board"].get_height())[
            #     "board"
            # ].get_height()
            # lowest = [x for x in lowest_holes if x["board"].get_height() == min_height]

            # # Get highest score of those lowest perms
            # best = max(lowest_holes, key=lambda x: x["board"].score)
            # return best["moves"]

            perms.sort(
                key=lambda perm: (perm["board"].score * 100)
                / ((perm["board"].count_holes() + 1) * 50)
                / ((perm["board"].get_height() + 1) * 1),
                reverse=True,
            )
            return perms[0]["moves"]
        return []

    def find_permutations(self, board: Board):
        permutations = []

        ## APPROACH 1

        # working_board = board.copy()
        # # force active piece to left side of board
        # # minimum moves to ensure a piece is as far left as it can go is 9
        # movements: list[int | str] = ["LEFT" for _ in range(9)]
        # working_board.input(movements)
        # for x in range(10):
        #     for r in range(4):
        #         # add all rotational permutations of the active piece
        #         temp_board = working_board.copy()
        #         temp_board.input("HARDDROP")
        #         temp_movements = deepcopy(movements)
        #         temp_movements.append("HARDDROP")
        #         permutations.append(
        #             {
        #                 "moves": temp_movements,
        #                 "board": temp_board,
        #             }
        #         )
        #         if not min(
        #             working_board.input("ROT_ANTICLOCKWISE"), key=lambda i: bool(i)
        #         ):
        #             # break if rotation fails
        #             break
        #         else:
        #             movements.append("ROT_ANTICLOCKWISE")
        #     # move piece to the right
        #     if not min(working_board.input("RIGHT"), key=lambda i: bool(i)):
        #         # break if movement fails
        #         break
        #     else:
        #         movements.append("RIGHT")

        ## APPROACH 2

        hardleft = ["LEFT" for _ in range(self.board.width)]

        # each possible column
        for x in range(self.board.width):
            column = ["RIGHT"] * x

            for moveset in [
                [],
                ["ROT_ANTICLOCKWISE"],
                ["ROT_CLOCKWISE"],
                ["ROT_CLOCKWISE", "ROT_CLOCKWISE"],
            ]:
                moves = column + moveset + ["HARDDROP"]
                temp_board = board.copy()
                # if none of the moves failed, add this permutation
                temp_board.input(hardleft)
                # print(temp_board.input(moves))
                if min(temp_board.input(moves), key=lambda i: bool(i)):
                    permutations.append(
                        {"board": temp_board, "moves": hardleft + moves}
                    )

        # remove any duplicate permutations
        perm_board_states = [q["board"].board for q in permutations]
        return [
            p
            for i, p in enumerate(permutations)
            if not p["board"].board in perm_board_states[:i:]
        ]


if __name__ == "__main__":
    pg.init()
    win = pg.display.set_mode((500, 700), pg.RESIZABLE)
    clock = pg.time.Clock()
    client = TetrisClientV1(board=Board(width=20, height=30))
    # client = TetrisClientV1(Board())
    elements = pg.sprite.Group(
        NextPieceDisplay(client.board), ScoreDisplay(client.board)
    )
    # client.find_permutations(client.board)
    while True:
        # clock.tick(4)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()

        win.fill("gray")

        client.move()
        client.update()
        elements.update()
        client.draw(win)
        elements.draw(win)
        pg.display.update()
