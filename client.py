from copy import deepcopy
from typing import Sequence
from main import Board, PieceDisplay, ScoreDisplay
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
                key=lambda perm: (perm["board"].score * 50)
                / ((perm["board"].count_holes() + 1) * 100)
                / ((perm["board"].get_height() + 1) * 1),
                reverse=True,
            )
            return perms[0]["moves"]
        return []

    def find_permutations(self, board: Board):
        permutations = []

        hardleft = ["LEFT" for _ in range(self.board.width)]

        # each possible column
        for x in range(self.board.width):
            column = ["RIGHT"] * x

            for moveset in [
                [],
                ["ROT_ANTICLOCKWISE"],
                ["ROT_CLOCKWISE"],
                ["ROT_CLOCKWISE", "ROT_CLOCKWISE"],
                ["HOLD"],
                ["HOLD", "ROT_ANTICLOCKWISE"],
                ["HOLD", "ROT_CLOCKWISE"],
                ["HOLD", "ROT_CLOCKWISE", "ROT_CLOCKWISE"],
            ]:
                temp_board = board.copy()
                # if none of the moves failed, add this permutation
                if min(temp_board.input(moveset), key=lambda i: bool(i), default=True):
                    temp_board.input(hardleft)
                    if min(
                        temp_board.input(column), key=lambda i: bool(i), default=True
                    ):
                        temp_board.input("HARDDROP")
                        permutations.append(
                            {
                                "board": temp_board,
                                "moves": moveset + hardleft + column + ["HARDDROP"],
                            }
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
    win = pg.display.set_mode((700, 700), pg.RESIZABLE)
    clock = pg.time.Clock()
    client = TetrisClientV1(board=Board())
    # client = TetrisClientV1(Board())
    elements = pg.sprite.Group(
        PieceDisplay(client.board),
        PieceDisplay(client.board, type="saved"),
        ScoreDisplay(client.board),
    )
    # client.find_permutations(client.board)
    while True:
        # clock.tick(4)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()

        win.fill("gray")
        print(client.board.saved_piece)

        client.move()
        client.update()
        elements.update()
        client.draw(win)
        elements.draw(win)
        pg.display.update()
