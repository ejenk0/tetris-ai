from client import TetrisClient
import pygame as pg
from main import Board, PieceDisplay, ScoreDisplay


class VisualTetrisClient(TetrisClient):
    def draw(self, surf: pg.surface.Surface):
        pg.sprite.GroupSingle(self.board).draw(surf)


if __name__ == "__main__":
    pg.init()
    win = pg.display.set_mode((700, 700), pg.RESIZABLE)
    clock = pg.time.Clock()
    client = VisualTetrisClient(board=Board())
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

        client.move()
        client.update()
        elements.update()
        client.draw(win)
        elements.draw(win)
        pg.display.update()
