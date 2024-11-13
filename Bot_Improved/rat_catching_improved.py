from env_utils import *
from bot_movement import *
import math
import random
import numpy as np

#The rat can only occupy an open cell
def list_possible_cells(grid, n):
    possible_cells = []
    for i in range(n):
        for j in range(n):
            #0 = open 2 = Rat 3 = Bot
            if grid[i][j] == 0 or grid[i][j]==2:
                possible_cells.append((i, j))
    return possible_cells

def is_possible_cell(grid, i, j):
    return grid[i][j] == 0 or grid[i][j] == 2

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

def init_prob_cells(grid, n, list_poss_cells):
    new_grid = np.copy(grid)
    num_possible_cells = len(list_poss_cells)
    # print(num_possible_cells)
    init_value = 1/num_possible_cells
    # print(init_value)
    for cell in list_poss_cells:
        new_grid[cell[0]][cell[1]] = init_value
    return new_grid

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

#We will partition the grid into 4 quadrants
def partition_grid(grid, n):
    quadrants = {
        'Q1': [],
        'Q2': [],
        'Q3': [],
        'Q4': []
    }

    mid = n//2

    for i in range(mid):
        for j in range(mid):
            if is_possible_cell(grid, i, j):
                quadrants['Q1'].append((i, j))

    for i in range(mid):
        for j in range(mid, n):
            if is_possible_cell(grid, i, j):
                quadrants['Q2'].append((i, j))
    
    for i in range(mid, n):
        for j in range(mid):
            if is_possible_cell(grid, i, j):
                quadrants['Q3'].append((i,j))
    
    for i in range(mid, n):
        for j in range(mid, n):
            if is_possible_cell(grid, i, j):
                quadrants['Q4'].append((i, j))
    
    return quadrants
  
def update_probabilities(prob_grid, prob_grid_dict, alpha, hear_prob, bot_pos, grid_for_map):
    quadrant_probabilities = {
        'Q1': 0.0,
        'Q2': 0.0,
        'Q3': 0.0,
        'Q4': 0.0
    }
    total_prob_sensor = 0.0
    prob_ping_values = {}
    new_prob_grid = np.copy(prob_grid)

    if hear_prob:
        for quadrant, cells in prob_grid_dict.items():
            for cell in cells:
                total_prob_sensor += prob_ping_j(bot_pos, cell, alpha) * new_prob_grid[cell[0]][cell[1]]
    elif not hear_prob:
        for quadrant, cells in prob_grid_dict.items():
            for cell in cells:
                total_prob_sensor += (1-prob_ping_j(bot_pos, cell, alpha)) * new_prob_grid[cell[0]][cell[1]]

    if total_prob_sensor != 0:
        if hear_prob:
            for quadrant, cells in prob_grid_dict.items():
                for cell in cells:
                    p_ping_j_val = prob_ping_j(bot_pos, cell, alpha)
                    updated_p = (p_ping_j_val * new_prob_grid[cell[0]][cell[1]])
                    new_prob_grid[cell[0]][cell[1]] = updated_p
                    quadrant_probabilities[quadrant] += updated_p
        else:
            for quadrant, cells in prob_grid_dict.items():
                for cell in cells:
                    p_ping_j_val = (1 - prob_ping_j(bot_pos, cell, alpha))
                    updated_p = (p_ping_j_val * new_prob_grid[cell[0]][cell[1]])
                    new_prob_grid[cell[0]][cell[1]] = updated_p
                    quadrant_probabilities[quadrant] += updated_p


    #Normalization
    total_quadrant_prob = sum(quadrant_probabilities.values())
    if total_quadrant_prob > 0:
        for quadrant in quadrant_probabilities:
            quadrant_probabilities[quadrant] /= total_quadrant_prob
    else:
        print("Total quadrant probability is zero. Normalization skipped.")
    
    return quadrant_probabilities

def weighted_center(target_quadrant, prob_grid_dict, prob_grid):
    sum_x = 0.0
    sum_y = 0.0
    sum_p = 0.0

    for cell in prob_grid_dict[target_quadrant]:
        i, j = cell
        p = prob_grid[i][j]
        sum_x += p * i
        sum_y += p * j
        sum_p += p
        print(sum_x, sum_y, sum_p)


    if sum_p > 0:
        x_c = sum_x/sum_p
        y_c = sum_y/sum_p
        x_final = int(round(x_c))
        y_final = int(round(y_c))
        target_cell = (x_final, y_final)
    return target_cell       

def main_improved(grid, n, bot_pos, rat_pos, alpha):
    frames_grid = []
    grid_for_map = np.copy(grid)
    # print(grid_for_map)
    frames_grid.append(np.copy(grid_for_map))
    grid_for_prob = np.zeros_like(grid, dtype=float)
    init_kb = list_possible_cells(grid_for_map, n)
    prob_grid = init_prob_cells(grid_for_prob, n, init_kb)
    prob_grid_dict = partition_grid(grid_for_map, n)
    # print(prob_grid)
    switch = True
    threshold = 0.3
    t = 0
    while t<5:
        if switch:
            hear_prob_from_rat = prob_ping_rat(bot_pos, rat_pos, alpha)
            print(hear_prob_from_rat)
            quadrant_probabilities = update_probabilities(prob_grid, prob_grid_dict, alpha, hear_prob_from_rat, bot_pos, grid_for_map)
            high_quadrants = {q: p for q, p in quadrant_probabilities.items()}

            if high_quadrants:
                target_quadrant = max(high_quadrants, key=high_quadrants.get)
                print(f"Target quadrant: {target_quadrant}")

                target_cell = weighted_center(target_quadrant, prob_grid_dict, prob_grid)
                print(f"Weighted center of selected quadrant: {target_cell}")

                if 0 <= target_cell[0] < n and 0 <= target_cell[1] < n and grid_for_map[target_cell[0]][target_cell[1]] != -1:
        t+=1