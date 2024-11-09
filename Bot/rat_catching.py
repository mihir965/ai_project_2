import env_utils
import math
import random

# The rat can only occupy an open cell
def list_possible_cells(grid, n):
    possible_cells = []
    for i in range(n):
        for j in range(n):
            if grid[i][j] == 0 or 2 or 4:
                possible_cells.append((i, j))
    return possible_cells

def manhattan_dist(bot_pos, rat_pos):
    return abs(bot_pos[0] - rat_pos[0]) + abs(bot_pos[1] - rat_pos[1])

#P(ping|d(i,j)) = e^{-a(d(i,j)-1)}
def prob_ping(bot_pos, j, alpha):
    dist = manhattan_dist(bot_pos, j)
    exponent = -1*(alpha*(dist-1))
    prob = math.exp(exponent)
    rand_chance = random.uniform(0.0, 1.0)
    print(prob)
    print(rand_chance)
    if prob>=rand_chance:
        return True
    else:
        return False

def main_function_catching(grid, n, bot_pos, rat_pos, alpha):
    list_possible_cells(grid, n)
    hear_prob=prob_ping(bot_pos, rat_pos, alpha)
    print(hear_prob)
    #Until the bot doesn't hear a ping from any cell, the bot will move towards the center of the grid.
    if not hear_prob:
        print("The bot will keep moving towards the center")
