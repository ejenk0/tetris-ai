from multiprocessing import Pool
import random
from main import Board
from client import TetrisClient


def test(index):
    random.seed(index)
    board = Board()
    client = TetrisClient(board)
    while not board.defeated:
        client.move()
    print(index, board.score)
    return board.score


if __name__ == "__main__":
    with Pool(8) as pool:
        pool.map(test, range(16))
