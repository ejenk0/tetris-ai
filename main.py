import math
from typing import Sequence
import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame as pg
import random


class Board(pg.sprite.Sprite):
    """
    Board class for containing the tetris board.
    """

    def __init__(
        self,
        width: int = 10,
        height: int = 20,
        board: list[list[pg.Color | None]] | None = None,
    ):
        self.pieces = {
            "I": {
                "symmetery": 2,
                "shape": [[0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0]],
                "colour": "cyan",
            },
            "L": {
                "symmetery": 4,
                "shape": [[0, 1, 0], [0, 1, 0], [0, 1, 1]],
                "colour": pg.Color("orange"),
            },
            "R": {
                "symmetery": 4,
                "shape": [[0, 1, 1], [0, 1, 0], [0, 1, 0]],
                "colour": pg.Color("blue"),
            },
            "T": {
                "symmetery": 4,
                "shape": [[0, 1, 0], [1, 1, 1]],
                "colour": pg.Color("purple"),
            },
            "Z": {
                "symmetery": 2,
                "shape": [[1, 1, 0], [0, 1, 1]],
                "colour": pg.Color("red"),
            },
            "S": {
                "symmetery": 2,
                "shape": [[0, 1, 1], [1, 1, 0]],
                "colour": pg.Color("green"),
            },
            "O": {
                "symmetery": 1,
                "shape": [[1, 1, 0], [1, 1, 0]],
                "colour": pg.Color("yellow"),
            },
        }

        # self.pieces = {
        #     "DOT": {
        #         "symmetery": 2,
        #         "shape": [[0, 1, 0], [0, 1, 0], [0, 1, 0]],
        #         "colour": "cyan",
        #     },
        #     "ARCH": {
        #         "symmetery": 4,
        #         "shape": [[0, 1, 1], [0, 1, 0], [0, 1, 1]],
        #         "colour": "orange",
        #     },
        #     "BITS": {
        #         "symmetery": 4,
        #         "shape": [[1, 0, 0], [1, 0, 1], [0, 0, 1]],
        #         "colour": "purple",
        #     },
        # }
        self.width = width
        self.height = height
        self.board: list[list[pg.Color | None]]
        if board:
            self.board = board
        else:
            self.board = [[None for x in range(self.width)] for y in range(self.height)]
        win = pg.display.get_surface()
        if win:
            super().__init__()
        self.active_coords: list[tuple[int, int]] | None = None
        self.saved_piece: dict | None = None
        self.score: int = 0
        self.difficult_combo = 0
        self.total_pieces = 0
        self.hold_used = False
        self.defeated = False
        self.pick_next_piece()
        self.rect: pg.rect.Rect = pg.Rect(0, 0, 0, 0)
        self.update()

    def update(self, tick=False):
        # GRAPHICS
        win = pg.display.get_surface()
        if win:
            self.square_size = int(win.get_height() / (self.height + 1))
            if self.square_size * self.width + 60 > win.get_width():
                self.square_size = int(win.get_width() / (self.width + 4))

            self.image = pg.Surface(
                (self.square_size * self.width, self.square_size * self.height)
            )
            # BG colour
            self.image.fill("lightgray")
            # Border colour
            pg.draw.rect(self.image, "black", self.image.get_rect(), 1)

            # Draw grid
            for col in range(1, self.width):
                pg.draw.line(
                    self.image,
                    "darkgray",
                    (col * self.square_size, 1),
                    (col * self.square_size, self.image.get_height() - 1),
                )
            for row in range(1, self.height):
                pg.draw.line(
                    self.image,
                    "darkgray",
                    (1, row * self.square_size),
                    (self.image.get_width() - 1, row * self.square_size),
                )

            # Draw pieces
            # self.boards is assumed to be a 2D array with elements of pg.Color or None
            for rownum, row in enumerate(self.board):
                for colnum, cell in enumerate(row):
                    if cell:
                        pg.draw.rect(
                            self.image,
                            cell,
                            (
                                int(colnum * self.square_size),
                                int(rownum * self.square_size),
                                math.ceil(self.square_size),
                                math.ceil(self.square_size),
                            ),
                            border_radius=int(self.square_size / 5),
                        )
                        pg.draw.rect(
                            self.image,
                            (0, 0, 0),
                            (
                                int(colnum * self.square_size),
                                int(rownum * self.square_size),
                                math.ceil(self.square_size),
                                math.ceil(self.square_size),
                            ),
                            width=max(1, int(self.square_size / 15)),
                            border_radius=int(self.square_size / 5),
                        )

            # DEV (Display current piece real position)
            # if self.current_piece:
            #     for coord in self.current_piece:
            #         pg.draw.rect(
            #             self.image,
            #             "purple",
            #             (
            #                 int(coord[1] * square_size),
            #                 int(coord[0] * square_size),
            #                 int(square_size / 2),
            #                 int(square_size / 2),
            #             ),
            #         )

            self.rect = self.image.get_rect()
            self.rect.center = win.get_rect().center

        # GAME LOGIC

        # clear lines and score
        cleared_lines = 0
        for rowindex, row in enumerate(self.board):
            if all(row):
                self.board.pop(rowindex)
                self.board.insert(0, [None for x in range(self.width)])
                cleared_lines += 1
        # increase the combo if a tetris is scored
        if cleared_lines == 4:
            self.difficult_combo += 1
        elif cleared_lines:
            self.difficult_combo = 0
        if cleared_lines:
            scoring = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}
            perfect_clear_scoring = {0: 0, 1: 800, 2: 1200, 3: 1800, 4: 2000}
            # perfect clear
            if not any(self.board[-1]):
                # back to back tetris perfect clear
                if self.difficult_combo >= 2:
                    self.score += 3200
                else:
                    self.score += perfect_clear_scoring[cleared_lines]
            # normal clear
            else:
                self.score += int(
                    scoring[cleared_lines] * (1.5 if self.difficult_combo >= 2 else 1)
                )

        if not self.active_coords:
            self.spawn(self.next_piece)
            self.total_pieces += 1
            self.pick_next_piece()
            self.hold_used = False

        if tick and self.active_coords:
            self.input("GRAVITY")

    def input(self, key: int | str | Sequence[int | str], update: bool = True):

        # If only one key was given, convert to list
        keys = [key] if type(key) is not list else key
        # print(keys)

        successes = []

        for key in keys:
            horiz = 0
            verti = 0
            rot = 0
            if key == "RIGHT" or key == pg.K_RIGHT or key == pg.K_d:
                horiz += 1
            if key == "LEFT" or key == pg.K_LEFT or key == pg.K_a:
                horiz -= 1
            if key == "GRAVITY":
                verti += 1
            if key == "HARDDROP" or key == pg.K_SPACE:
                while self.active_coords:
                    self.input("GRAVITY", update=False)
                    self.score += 2
            if key == "ROT_CLOCKWISE" or key == pg.K_UP or key == pg.K_x:
                rot -= 1
            if key == "ROT_ANTICLOCKWISE" or key == pg.K_z:
                rot += 1

            if (
                (key == "HOLD" or key == pg.K_c)
                and self.active_coords
                and not self.hold_used
            ):
                self.hold_used = True
                old_piece = self.current_piece

                # wipe the old piece from the board
                for coord in self.active_coords:
                    self.board[coord[0]][coord[1]] = None

                if self.saved_piece:
                    self.spawn(self.saved_piece)
                else:
                    self.spawn(self.next_piece)
                    self.total_pieces += 1
                    self.pick_next_piece()

                self.saved_piece = old_piece

            if self.active_coords:
                # Rotate the piece if we need to
                if rot:
                    self.rotate(rot)
                # Check each tile to see if we can move
                can_move = True
                for coord in self.active_coords:
                    if (
                        coord[0] + verti >= self.height
                        or coord[0] + verti < 0
                        or coord[1] + horiz < 0
                        or coord[1] + horiz >= self.width
                    ):
                        can_move = False
                        break
                    elif (
                        self.board[coord[0] + verti][coord[1] + horiz]
                        and (coord[0] + verti, coord[1] + horiz)
                        not in self.active_coords
                    ):
                        can_move = False
                        break

                # If we can move, update self.current_piece and self.board
                if can_move:
                    repositioned_piece: list[tuple[int, int]] = []
                    for coord in self.active_coords:
                        self.board[coord[0] + verti][coord[1] + horiz] = self.board[
                            coord[0]
                        ][coord[1]]
                        if (
                            not (coord[0] - verti, coord[1] - horiz)
                            in self.active_coords
                        ):
                            self.board[coord[0]][coord[1]] = None
                        repositioned_piece.append((coord[0] + verti, coord[1] + horiz))
                    self.active_coords = repositioned_piece
                    successes.append(True)
                elif key == "GRAVITY":
                    self.active_coords = None

                if not can_move:
                    successes.append(False)
            else:
                if key == "HARDDROP" or key == pg.K_SPACE:
                    successes.append(True)
                else:
                    successes.append(False)

        if update:
            self.update(tick=False)
        return successes

    def rotate(self, rotation):
        if not self.active_coords:
            return

        # convert negative rotations into positive
        while rotation < 0:
            rotation += 4

        rotation %= 4

        for _ in range(abs(rotation)):
            rowoffset = min(self.active_coords, key=lambda x: x[0])[0]
            coloffset = min(self.active_coords, key=lambda x: x[1])[1]

            rowheight = max(self.active_coords, key=lambda x: x[0])[0] - rowoffset + 1
            colwidth = max(self.active_coords, key=lambda x: x[1])[1] - coloffset + 1

            piece_array: list[list[bool]] = [
                [False for _ in range(colwidth)] for _ in range(rowheight)
            ]
            for coord in self.active_coords:
                piece_array[coord[0] - rowoffset][coord[1] - coloffset] = True

            rotated_piece = []

            for rowindex, row in enumerate(piece_array):
                row.reverse()
                for colindex, cell in enumerate(row):
                    if cell:
                        # this is where the piece is transposed
                        rotated_piece.append(
                            (colindex + rowoffset, rowindex + coloffset)
                        )

            can_move = True
            for index, coord in enumerate(rotated_piece):
                if (
                    coord[0] >= self.height
                    or coord[0] < 0
                    or coord[1] < 0
                    or coord[1] >= self.width
                ):
                    can_move = False
                    break
                elif (
                    self.board[coord[0]][coord[1]]
                    and (coord[0], coord[1]) not in self.active_coords
                ):
                    can_move = False
                    break

            if can_move:
                # sample colour from old piece
                col = self.board[self.active_coords[0][0]][self.active_coords[0][1]]
                for coord in self.active_coords:
                    self.board[coord[0]][coord[1]] = None
                for coord in rotated_piece:
                    self.board[coord[0]][coord[1]] = col

                self.active_coords = rotated_piece

    def pick_next_piece(self):
        # random.seed(1 * self.total_pieces)
        self.next_piece = random.choice(list(self.pieces.values()))

    def spawn(self, piece: dict):
        """
        Checks and spawns a piece if it can.
        Sets self.current_piece to the new piece and
        self.active_coords to the new piece's active coordinates.

        piece: {
            "shape": [[0, 1, 0], ... ],
            "colour": "red",
        }
        """
        self.active_coords = []
        # check for collisions in the spawning area
        for rownum, row in enumerate(piece["shape"]):
            for colnum, cell in enumerate(row):
                if cell and self.board[rownum][colnum + int(self.width / 2) - 1]:
                    self.defeated = True
                    return
        self.current_piece = piece.copy()
        # spawn new piece
        for rownum, row in enumerate(piece["shape"]):
            for colnum, cell in enumerate(row):
                if cell:
                    self.board[rownum][colnum + int(self.width / 2) - 1] = piece[
                        "colour"
                    ]
                    self.active_coords.append(
                        (rownum, colnum + int(self.width / 2) - 1)
                    )

    def get_height(self):
        fixed_board = board_array_copy(self.board)
        if self.active_coords:
            for coord in self.active_coords:
                fixed_board[coord[0]][coord[1]] = None
        empty_lines = 0
        for row in fixed_board:
            # if this is an empty line
            if not any(row):
                empty_lines += 1
        return self.height - empty_lines

    def count_holes(self):
        fixed_board = board_array_copy(self.board)
        if self.active_coords:
            for coord in self.active_coords:
                fixed_board[coord[0]][coord[1]] = None
        count = 0
        for rowindex, row in enumerate(fixed_board):
            if rowindex >= 1:
                for colindex, cell in enumerate(row):
                    if (fixed_board[rowindex - 1][colindex]) and not cell:
                        count += 1
        return count

    def count_wells(self):
        fixed_board = board_array_copy(self.board)
        if self.active_coords:
            for coord in self.active_coords:
                fixed_board[coord[0]][coord[1]] = None
        count = 0
        for rowindex, row in enumerate(fixed_board):
            if rowindex >= 4 and rowindex < self.height:
                for colindex, cell in enumerate(row):
                    # If this cell is empty and there is a cell below and
                    # two empty cells above and cells to either side
                    if (
                        (not cell)
                        and (
                            rowindex == self.height - 1
                            or fixed_board[rowindex + 1][colindex]
                        )
                        and (not fixed_board[rowindex - 1][colindex])
                        and (
                            colindex == (self.width - 1)
                            or fixed_board[rowindex - 1][colindex + 1]
                        )
                        and (colindex == 0 or fixed_board[rowindex - 1][colindex - 1])
                        and (not fixed_board[rowindex - 2][colindex])
                        and (
                            colindex == (self.width - 1)
                            or fixed_board[rowindex - 2][colindex + 1]
                        )
                        and (colindex == 0 or fixed_board[rowindex - 2][colindex - 1])
                    ):
                        count += 1
        return count

    def game_over(self):
        # TODO: Game over events
        print("GAME OVER")

    def copy(self):
        copied_obj = Board(
            width=self.width, height=self.height, board=board_array_copy(self.board)
        )
        if self.active_coords:
            copied_obj.active_coords = self.active_coords.copy()
        copied_obj.current_piece = self.current_piece.copy()
        copied_obj.next_piece = self.next_piece.copy()
        if self.saved_piece:
            copied_obj.saved_piece = self.saved_piece.copy()
        copied_obj.score = self.score
        copied_obj.difficult_combo = self.difficult_combo
        copied_obj.total_pieces = self.total_pieces
        return copied_obj


class PieceDisplay(pg.sprite.Sprite):
    def __init__(self, board: Board, type: str = "next"):
        super().__init__()
        self.board = board
        self.type = type
        self.update()

    def update(self, tick=False):
        win = pg.display.get_surface()
        self.image = pg.Surface((win.get_height() * 0.1, win.get_height() * 0.3))
        self.image.fill("grey")
        self.rect = self.image.get_rect()
        if self.type == "next":
            self.rect.topleft = self.board.rect.topright
            self.rect.top += 10
            self.rect.left += 10
        else:
            self.rect.topright = self.board.rect.topleft
            self.rect.top += 60
            self.rect.right -= 10

        square_size = int(self.board.square_size * 2 / 3)
        piece = self.board.next_piece if self.type == "next" else self.board.saved_piece
        if piece:
            for rownum, row in enumerate(piece["shape"]):
                for colnum, cell in enumerate(row):
                    if cell:
                        pg.draw.rect(
                            self.image,
                            piece["colour"],
                            (
                                int(colnum * square_size),
                                int(rownum * square_size),
                                math.ceil(square_size),
                                math.ceil(square_size),
                            ),
                            border_radius=int(square_size / 5),
                        )
                        pg.draw.rect(
                            self.image,
                            (0, 0, 0),
                            (
                                int(colnum * square_size),
                                int(rownum * square_size),
                                math.ceil(square_size),
                                math.ceil(square_size),
                            ),
                            width=max(1, int(square_size / 15)),
                            border_radius=int(square_size / 5),
                        )


class ScoreDisplay(pg.sprite.Sprite):
    def __init__(self, board: Board):
        super().__init__()
        self.board = board
        self.update()

    def update(self, tick=False):
        win = pg.display.get_surface()
        self.image = pg.font.SysFont("Arial", int(win.get_height() * 0.025)).render(
            f"{self.board.score}", True, (0, 0, 0)
        )
        self.rect = self.image.get_rect()
        self.rect.topright = self.board.rect.topleft
        self.rect.top += 10
        self.rect.right -= 10


def board_array_copy(board: list[list[None | pg.Color]]):
    # return copy.deepcopy(board)
    return [x.copy() for x in board]


if __name__ == "__main__":
    pg.init()

    # Setup
    WIN = pg.display.set_mode((500, 700), pg.RESIZABLE)
    clock = pg.time.Clock()
    BOARD = Board()

    elements = pg.sprite.Group(
        BOARD,
        PieceDisplay(BOARD, type="next"),
        PieceDisplay(BOARD, type="saved"),
        ScoreDisplay(BOARD),
    )

    time_since_tick = 0
    speed = 500  # milliseconds per tick

    paused = False
    while True:
        clock.tick(60)
        if not paused:
            time_since_tick += clock.get_time()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    paused = not paused
                elif not paused:
                    BOARD.input(event.key)
                if event.key == pg.K_DOWN:
                    speed = 50
            if event.type == pg.KEYUP:
                if event.key == pg.K_DOWN:
                    speed = 500

        WIN.fill("gray")
        # print(BOARD.get_height())

        if time_since_tick > speed:
            tick = True
            time_since_tick = 0
        else:
            tick = False

        elements.update(tick=tick)
        elements.draw(WIN)

        pg.display.flip()
