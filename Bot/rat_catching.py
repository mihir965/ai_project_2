from env_utils import *
from bot_movement import *
import math
import random
import numpy as np

# The rat can only occupy an open cell
def list_possible_cells(grid, n):
    possible_cells = []
    for i in range(n):
        for j in range(n):
            #0 = open 2 = Rat 3 = Bot
            if grid[i][j] == 0 or grid[i][j]==2:
                possible_cells.append((i, j))
    return possible_cells

def manhattan_dist(bot_pos, j):
    return abs(bot_pos[0] - j[0]) + abs(bot_pos[1] - j[1])

#P(ping|d(i,j)) = e^{-a(d(i,j)-1)}
def prob_ping_rat(bot_pos, rat_pos, alpha):
    # dist = manhattan_dist(bot_pos, rat_pos)
    dist = max(1, manhattan_dist(bot_pos, rat_pos))
    exponent = -1*(alpha*(dist-1))
    prob = math.exp(exponent)
    rand_chance = random.uniform(0.0, 1.0)
    # print(prob)
    # print(rand_chance)
    if prob>=rand_chance:
        return True
    else:
        return False
    
def prob_ping_j(bot_pos, j, alpha):
    # dist = manhattan_dist(bot_pos, j)
    dist = max(1, manhattan_dist(bot_pos, j))
    exponent = -1*(alpha*(dist-1))
    prob = math.exp(exponent)
    return prob
    
def update_cells(prob_grid, kb, hear_prob, bot_pos, alpha):
    new_prob_grid = np.copy(prob_grid)
    total_prob_sensor = 0
    if hear_prob:
        for cell in kb:
            total_prob_sensor += prob_ping_j(bot_pos, cell, alpha)*new_prob_grid[cell[0]][cell[1]]
    elif not hear_prob:
        for cell in kb:
            total_prob_sensor += (1-prob_ping_j(bot_pos, cell, alpha))*new_prob_grid[cell[0]][cell[1]]
    if hear_prob:
        #Just to ensure no division by 0
        if total_prob_sensor!=0:
            for cell in kb:
                new_prob_grid[cell[0]][cell[1]] = (prob_ping_j(bot_pos, cell, alpha)*new_prob_grid[cell[0]][cell[1]])/total_prob_sensor
    elif not hear_prob:
        if total_prob_sensor!=0:
            for cell in kb:
                new_prob_grid[cell[0]][cell[1]] = ((1-prob_ping_j(bot_pos, cell, alpha))*new_prob_grid[cell[0]][cell[1]])/total_prob_sensor
    # Normalize the probability grid
    total_prob = np.sum(new_prob_grid)
    if total_prob > 0:
        new_prob_grid = new_prob_grid / total_prob
    else:
        print("Total probability is zero after update.")

    return new_prob_grid

def init_prob_cells(grid, n, list_poss_cells):
    new_grid = np.copy(grid)
    num_possible_cells = len(list_poss_cells)
    # print(num_possible_cells)
    init_value = 1/num_possible_cells
    # print(init_value)
    for cell in list_poss_cells:
        new_grid[cell[0]][cell[1]] = init_value
    return new_grid

def main_function_catching(grid, n, bot_pos, rat_pos, alpha):
    frames_heatmap = []
    frames_grid = []
    grid_for_map = np.copy(grid)
    frames_grid.append(np.copy(grid_for_map))
    grid_for_prob = np.zeros_like(grid, dtype=float)
    init_kb = list_possible_cells(grid_for_map, n)
    prob_grid = init_prob_cells(grid_for_prob, n, init_kb)
    switch = True
    t = 0
    while True:
        if switch:
            # Use Rat detector to hear ping
            hear_prob_from_rat = prob_ping_rat(bot_pos, rat_pos, alpha)
            # Update the probabilities based on the sensor reading
            prob_grid = update_cells(prob_grid, init_kb, hear_prob_from_rat, bot_pos, alpha)
            # Get the cell with max probability
            max_prob = np.max(prob_grid)
            result = np.where(prob_grid == max_prob)
            max_cells = list(zip(result[0], result[1]))
            max_cells = [(int(row), int(col)) for row, col in max_cells]
            if max_prob == 1:
                print(f"The rat was found at cell: {max_cells[0]}")
        else:
            if not max_cells:
                break
            target_cell = max_cells[0]
            if bot_pos == target_cell:
                print("Bot is already at the target cell.")
                switch = True
                continue
            if grid_for_map[target_cell[0]][target_cell[1]] == -1:
                print(f"Target cell {target_cell} is blocked.")
                max_cells.remove(target_cell)
                if not max_cells:
                    print("No reachable cells with maximum probability.")
                    break
                continue
            path = plan_path_bot2(grid_for_map, bot_pos, target_cell, n)
            if path is None or len(path) <= 1:
                print("No path found to the target cell.")
                break
            # Update bot position
            grid_for_map[bot_pos[0]][bot_pos[1]] = 0 
            bot_pos = path[1]
            grid_for_map[bot_pos[0]][bot_pos[1]] = 3 
        frames_grid.append(np.copy(grid_for_map))
        t += 1
        switch = not switch

        if bot_pos == rat_pos:
            print(f"Probability at rat's position ({rat_pos}): {prob_grid[rat_pos[0]][rat_pos[1]]}")
            print("Bot has caught the rat")
            break
    print(f"Total steps taken: {t}")
    visualize_simulation_1(frames_grid)
