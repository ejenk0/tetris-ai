from multiprocessing import Pool
import random
from typing import Sequence


class TetrisClient:
    def __init__(
        self,
        board,
        weights: Sequence[float] = [1.58865303, 0.3142535, 1.24303428, 0.81636418],
        # weights: Sequence[float] = [1.588, 0.45, 1.243, 0.816],
        # weights: Sequence[float] = [0.000000001, 1, 0, 1],
    ):
        self.weights = weights
        self.board = board

    def update(self, tick: bool = False):
        self.board.update(tick=tick)

    def move(self):
        """
        Calculate and make best move
        """
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
                key=lambda perm: perm["board"].defeated
                * ((perm["board"].score * self.weights[0]))
                / ((perm["board"].count_holes() * self.weights[1]) + 1)
                / ((perm["board"].get_height() * self.weights[2]) + 1)
                / (((max(perm["board"].count_wells(), 1) - 1) * self.weights[3]) + 1),
                reverse=True,
            )
            return perms[0]["moves"]
        return []

    def find_permutations(self, board):
        permutations = []

        hardleft = ["LEFT" for _ in range(self.board.width)]

        # each possible column
        for x in range(self.board.width):
            column = ["RIGHT"] * x
            movesets = [[], ["HOLD"]]

            if board.current_piece["symmetery"] > 1:
                movesets += [
                    ["ROT_ANTICLOCKWISE"],
                ]
                if board.current_piece["symmetery"] > 2:
                    movesets += [["ROT_CLOCKWISE"], ["ROT_CLOCKWISE", "ROT_CLOCKWISE"]]

            if board.saved_piece:
                if board.saved_piece["symmetery"] > 1:
                    movesets += [
                        ["HOLD", "ROT_ANTICLOCKWISE"],
                    ]
                    if board.saved_piece["symmetery"] > 2:
                        movesets += [
                            ["HOLD", "ROT_CLOCKWISE"],
                            ["HOLD", "ROT_CLOCKWISE", "ROT_CLOCKWISE"],
                        ]
            else:
                movesets += [
                    ["HOLD", "ROT_ANTICLOCKWISE"],
                    ["HOLD", "ROT_CLOCKWISE"],
                    ["HOLD", "ROT_CLOCKWISE", "ROT_CLOCKWISE"],
                ]

            for moveset in movesets:
                temp_board = board.copy()
                # if none of the moves failed, add this permutation
                if all(temp_board.input(moveset, update=False)) or not moveset:
                    temp_board.input(hardleft, update=False)
                    if all(temp_board.input(column, update=False)) or not column:
                        temp_board.input("HARDDROP")
                        permutations.append(
                            {
                                "board": temp_board,
                                "moves": moveset + hardleft + column + ["HARDDROP"],
                            }
                        )

        return permutations
