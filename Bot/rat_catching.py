import env_utils
import math
import random
import numpy as np

# The rat can only occupy an open cell
def list_possible_cells(grid, n):
    possible_cells = []
    for i in range(n):
        for j in range(n):
            if grid[i][j] == 0 or grid[i][j]==2 or grid[i][j]==4:
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
    
# def update_cells(grid, list_possible_cells):
#     for i in list_possible_cells:


def init_prob_cells(grid, n, list_poss_cells):
    num_possible_cells = len(list_poss_cells)
    print(num_possible_cells)
    init_value = 1/num_possible_cells
    print(init_value)
    for cell in list_poss_cells:
        grid[cell[0]][cell[1]] = init_value
    return grid

def main_function_catching(grid, n, bot_pos, rat_pos, alpha):
    grid = np.array(grid, dtype=float)
    list_poss_cells = list_possible_cells(grid, n)
    print(list_poss_cells)
    hear_prob=prob_ping(bot_pos, rat_pos, alpha)
    print(hear_prob)
    #initialize the probabilities
    prob_grid = init_prob_cells(grid, n, list_poss_cells)
    print(prob_grid)
    print(prob_grid[2][4])
    #Until the bot doesn't hear a ping from any cell, the bot will move towards the center of the grid.
