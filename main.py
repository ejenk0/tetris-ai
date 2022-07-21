import copy
import math
from typing import Sequence
import pygame as pg
import random


class Board(pg.sprite.Sprite):
    """
    Board class for containing the tetris board.
    """

    def __init__(self, width: int = 10, height: int = 20):
        self.pieces = {
            "I": {
                "shape": [[0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0]],
                "colour": "cyan",
            },
            "L": {
                "shape": [[0, 1, 0], [0, 1, 0], [0, 1, 1]],
                "colour": pg.Color("orange"),
            },
            "R": {
                "shape": [[0, 1, 1], [0, 1, 0], [0, 1, 0]],
                "colour": pg.Color("blue"),
            },
            "T": {"shape": [[0, 1, 0], [1, 1, 1]], "colour": pg.Color("purple")},
            "Z": {"shape": [[1, 1, 0], [0, 1, 1]], "colour": pg.Color("red")},
            "S": {"shape": [[0, 1, 1], [1, 1, 0]], "colour": pg.Color("green")},
            "O": {"shape": [[1, 1, 0], [1, 1, 0]], "colour": pg.Color("yellow")},
        }
        self.width = width
        self.height = height
        self.board: list[list[pg.Color | None]] = [
            [None for x in range(self.width)] for y in range(self.height)
        ]
        super().__init__()
        self.current_piece: list[tuple[int, int]] | None = None
        self.score: int = 0
        self.difficult_combo = 0
        self.total_pieces = 0
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
            if min([bool(x) for x in row]):
                self.board.pop(rowindex)
                self.board.insert(0, [None for x in range(self.width)])
                cleared_lines += 1
        # increase the combo if a tetris is scored
        if cleared_lines == 4:
            self.difficult_combo += 1
        elif cleared_lines:
            self.difficult_combo = 0
        scoring = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}
        perfect_clear_scoring = {0: 0, 1: 800, 2: 1200, 3: 1800, 4: 2000}
        # perfect clear
        if min([bool(x) for x in self.board[-1]]):
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

        if not self.current_piece:
            self.current_piece = []
            # check for collisions in the spawning area
            for rownum, row in enumerate(self.next_piece["shape"]):
                for colnum, cell in enumerate(row):
                    if cell and self.board[rownum][colnum + int(self.width / 2) - 1]:
                        self.game_over()
                        return
            # spawn new piece
            for rownum, row in enumerate(self.next_piece["shape"]):
                for colnum, cell in enumerate(row):
                    if cell:
                        self.board[rownum][
                            colnum + int(self.width / 2) - 1
                        ] = self.next_piece["colour"]
                        self.current_piece.append(
                            (rownum, colnum + int(self.width / 2) - 1)
                        )
            self.total_pieces += 1

            self.pick_next_piece()

        if tick and self.current_piece:
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
                while self.current_piece:
                    self.input("GRAVITY", update=False)
                    self.score += 2
            if key == "ROT_CLOCKWISE" or key == pg.K_UP or key == pg.K_x:
                rot -= 1
            if key == "ROT_ANTICLOCKWISE" or key == pg.K_z:
                rot += 1

            if self.current_piece:
                # Rotate the piece if we need to
                if rot:
                    self.rotate(rot)
                # Check each tile to see if we can move
                can_move = True
                for coord in self.current_piece:
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
                        not in self.current_piece
                    ):
                        can_move = False
                        break

                # If we can move, update self.current_piece and self.board
                if can_move:
                    repositioned_piece: list[tuple[int, int]] = []
                    for coord in self.current_piece:
                        self.board[coord[0] + verti][coord[1] + horiz] = self.board[
                            coord[0]
                        ][coord[1]]
                        if (
                            not (coord[0] - verti, coord[1] - horiz)
                            in self.current_piece
                        ):
                            self.board[coord[0]][coord[1]] = None
                        repositioned_piece.append((coord[0] + verti, coord[1] + horiz))
                    self.current_piece = repositioned_piece
                    successes.append(True)
                elif key == "GRAVITY":
                    self.current_piece = None

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
        if not self.current_piece:
            return

        # convert negative rotations into positive
        while rotation < 0:
            rotation += 4

        rotation %= 4

        for _ in range(abs(rotation)):
            rowoffset = min(self.current_piece, key=lambda x: x[0])[0]
            coloffset = min(self.current_piece, key=lambda x: x[1])[1]

            rowheight = max(self.current_piece, key=lambda x: x[0])[0] - rowoffset + 1
            colwidth = max(self.current_piece, key=lambda x: x[1])[1] - coloffset + 1

            piece_array: list[list[bool]] = [
                [False for _ in range(colwidth)] for _ in range(rowheight)
            ]
            for coord in self.current_piece:
                piece_array[coord[0] - rowoffset][coord[1] - coloffset] = True

            # piece_array = [
            #     [piece_array[j][i] for j in range(len(piece_array))]
            #     for i in range(len(piece_array[0]))
            # ]
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
                    and (coord[0], coord[1]) not in self.current_piece
                ):
                    can_move = False
                    break

            if can_move:
                # sample colour from old piece
                col = self.board[self.current_piece[0][0]][self.current_piece[0][1]]
                for coord in self.current_piece:
                    self.board[coord[0]][coord[1]] = None
                for coord in rotated_piece:
                    self.board[coord[0]][coord[1]] = col

                self.current_piece = rotated_piece

    def pick_next_piece(self):
        random.seed()
        self.next_piece = random.choice(list(self.pieces.values()))

    def get_height(self):
        fixed_board = copy.deepcopy(self.board)
        if self.current_piece:
            for coord in self.current_piece:
                fixed_board[coord[0]][coord[1]] = None
        empty_lines = 0
        for row in fixed_board:
            if not max([bool(x) for x in row]):
                empty_lines += 1
        return self.height - empty_lines

    def count_holes(self):
        fixed_board = copy.deepcopy(self.board)
        if self.current_piece:
            for coord in self.current_piece:
                fixed_board[coord[0]][coord[1]] = None
        count = 0
        for rowindex, row in enumerate(fixed_board):
            for colindex, cell in enumerate(row):
                if rowindex >= 1:
                    if (not cell) and (fixed_board[rowindex - 1][colindex]):
                        count += 1
        return count

    def game_over(self):
        # TODO: Game over events
        print("GAME OVER")

    def copy(self):
        copied_obj = Board(width=self.width, height=self.height)
        copied_obj.board = copy.deepcopy(self.board)
        copied_obj.current_piece = copy.deepcopy(self.current_piece)
        copied_obj.next_piece = copy.deepcopy(self.next_piece)
        copied_obj.score = self.score
        copied_obj.difficult_combo = self.difficult_combo
        copied_obj.total_pieces = self.total_pieces
        return copied_obj


class NextPieceDisplay(pg.sprite.Sprite):
    def __init__(self, board: Board):
        super().__init__()
        self.board = board
        self.update()

    def update(self, tick=False):
        win = pg.display.get_surface()
        self.image = pg.Surface((win.get_height() * 0.3, win.get_height() * 0.3))
        self.image.fill("grey")
        self.rect = self.image.get_rect()
        self.rect.topleft = self.board.rect.topright
        self.rect.top += 10
        self.rect.left += 10

        square_size = int(self.board.square_size * 2 / 3)

        if self.board.next_piece:
            for rownum, row in enumerate(self.board.next_piece["shape"]):
                for colnum, cell in enumerate(row):
                    if cell:
                        pg.draw.rect(
                            self.image,
                            self.board.next_piece["colour"],
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


if __name__ == "__main__":
    pg.init()

    # Setup
    WIN = pg.display.set_mode((500, 700), pg.RESIZABLE)
    clock = pg.time.Clock()
    BOARD = Board(width=60)

    elements = pg.sprite.Group(BOARD, NextPieceDisplay(BOARD), ScoreDisplay(BOARD))

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