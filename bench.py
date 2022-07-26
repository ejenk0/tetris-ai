from multiprocessing import Pool
from main import Board
from client import TetrisClient


def test(index):
    board = Board()
    client = TetrisClient(board)
    while not board.defeated:
        client.move()
    print(index, board.score)
    return board.score


if __name__ == "__main__":

    with Pool(20) as pool:
        results = pool.map(test, range(20))
        print(sum(results) / len(results))
