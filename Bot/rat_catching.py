from env_utils import *
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

def manhattan_dist(bot_pos, j):
    return abs(bot_pos[0] - j[0]) + abs(bot_pos[1] - j[1])

#P(ping|d(i,j)) = e^{-a(d(i,j)-1)}
def prob_ping_rat(bot_pos, rat_pos, alpha):
    dist = manhattan_dist(bot_pos, rat_pos)
    exponent = -1*(alpha*(dist-1))
    prob = math.exp(exponent)
    rand_chance = random.uniform(0.0, 1.0)
    print(prob)
    print(rand_chance)
    if prob>=rand_chance:
        return True
    else:
        return False
    
def prob_ping_j(bot_pos, j, alpha):
    dist = manhattan_dist(bot_pos, j)
    exponent = -1*(alpha*(dist-1))
    prob = math.exp(exponent)
    rand_chance = random.uniform(0.0, 1.0)
    return prob
    
def update_cells(prob_grid, kb, hear_prob, bot_pos, alpha):
    total_prob_sensor = 0
    if hear_prob:
        for cell in kb:
            total_prob_sensor += prob_ping_j(bot_pos, cell, alpha)*prob_grid[cell[0]][cell[1]]
    elif not hear_prob:
        for cell in kb:
            total_prob_sensor += (1-prob_ping_j(bot_pos, cell, alpha))*prob_grid[cell[0]][cell[1]]
    if hear_prob:
        for cell in kb:
            prob_grid[cell[0]][cell[1]] = (prob_ping_j(bot_pos, cell, alpha)*prob_grid[cell[0]][cell[1]])/total_prob_sensor
    elif not hear_prob:
        for cell in kb:
            prob_grid[cell[0]][cell[1]] = ((1-prob_ping_j(bot_pos, cell, alpha))*prob_grid[cell[0]][cell[1]])/total_prob_sensor
    return prob_grid

def init_prob_cells(grid, n, list_poss_cells):
    num_possible_cells = len(list_poss_cells)
    # print(num_possible_cells)
    init_value = 1/num_possible_cells
    # print(init_value)
    for cell in list_poss_cells:
        grid[cell[0]][cell[1]] = init_value
    return grid

def main_function_catching(grid, n, bot_pos, rat_pos, alpha):
    frames = []
    grid = np.array(grid, dtype=float)
    list_poss_cells = list_possible_cells(grid, n)
    print(list_poss_cells)
    hear_prob=prob_ping_rat(bot_pos, rat_pos, alpha)
    print(hear_prob)
    #initialize the probabilities
    prob_grid = init_prob_cells(grid, n, list_poss_cells)
    # frames.append(np.copy(prob_grid))
    # visualize_simulation(frames)
    # print(prob_grid)
    # print(prob_grid[2][4])
    kb = list_poss_cells
    prob_grid = update_cells(prob_grid, kb, hear_prob, bot_pos, alpha)
    prob_2 = prob_grid.copy()
    max_prob = np.max(prob_grid)
    result = np.where(prob_grid==max_prob)
    max_cells = list(zip(result[0], result[1]))
    print([(int(row), int(col)) for row, col in max_cells])
    # print(prob_grid)
    # frames = []
    # frames.append(np.copy(prob_grid))
    # print(bot_pos)
    # print(rat_pos)
    # visualize_simulation(frames)