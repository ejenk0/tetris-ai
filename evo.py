# Best weights: [1.58865303 0.3142535  1.24303428 0.81636418]
# Best score: 250132.4

import pygad
import random
from client import TetrisClient
from main import Board


def main():
    bot = TetrisClient(Board())
    while not bot.board.defeated:
        bot.move()
    print(bot.board.score)


def fitness(weights, solution_idx):
    seed = random.random()
    random.seed(seed)
    scores = []
    for _ in range(15):
        bot = TetrisClient(Board(), weights)
        while not bot.board.defeated:
            bot.move()
        scores.append(bot.board.score)
    print(
        f"Solution {solution_idx}:\n Seed: {seed}\n Weights: {weights}\n Score: {sum(scores) / len(scores)}"
    )
    return sum(scores) / len(scores)


def on_generation(ga: pygad.GA):
    print(
        f"\nGeneration complete.\nBest weights: {ga.best_solution()[0]}\nBest score: {ga.best_solution()[1]}\n"
    )


if __name__ == "__main__":
    ga = pygad.GA(
        fitness_func=fitness,
        num_generations=40,
        num_parents_mating=3,
        on_generation=on_generation,
        sol_per_pop=15,
        num_genes=4,
        mutation_num_genes=2,
        init_range_low=0.5,
        init_range_high=1.5,
        parallel_processing=["process", 15],
        save_best_solutions=True,
    )
    ga.run()
    ga.plot_fitness()
    print("\nBest solution: ", ga.best_solution())
