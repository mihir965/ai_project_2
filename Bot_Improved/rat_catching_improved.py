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
  
def update_probabilities(prob_grid, prob_grid_dict, alpha, hear_prob, bot_pos):
    quadrant_probabilities = {
        'Q1': 0.0,
        'Q2': 0.0,
        'Q3': 0.0,
        'Q4': 0.0
    }
    total_prob_sensor = 0.0
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
                    updated_p = (p_ping_j_val * new_prob_grid[cell[0]][cell[1]])/total_prob_sensor
                    new_prob_grid[cell[0]][cell[1]] = updated_p
                    quadrant_probabilities[quadrant] += updated_p
        else:
            for quadrant, cells in prob_grid_dict.items():
                for cell in cells:
                    p_ping_j_val = (1 - prob_ping_j(bot_pos, cell, alpha))
                    updated_p = (p_ping_j_val * new_prob_grid[cell[0]][cell[1]])/total_prob_sensor
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

    print(f"Before anything see the probability grid of the target quadrant:\n{print(target_quadrant)}")

    for cell in prob_grid_dict[target_quadrant]:
        print(cell)
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
    else:
        target_cell = random.choice(prob_grid_dict[target_quadrant]) if prob_grid_dict[target_quadrant] else None
 
    return target_cell   

def movement(grid_for_map, target_cell, bot_pos, n, frames_grid):
    path = plan_path_bot2(grid_for_map, bot_pos, target_cell, n)
    went = 0
    if path and len(path)>1:
        halfway = len(path)//2
        print(path)
        print(f"Halfway is :{path[halfway]}")
        halfway_coordinates = path[halfway]
        while True:
            print(f"Went: {went}")
            old_pos = bot_pos
            grid_for_map[bot_pos[0]][bot_pos[1]] = 0
            bot_pos = path.pop(1)
            grid_for_map[bot_pos[0]][bot_pos[1]] = 3
            print(f"Moving bot from {old_pos} to {bot_pos}")
            if bot_pos==halfway_coordinates:
                break
            frames_grid.append(np.copy(grid_for_map))
            print(bot_pos)
            went+=1
        print(f"Moving bot from {old_pos} to {bot_pos}")
        frames_grid.append(np.copy(grid_for_map))
        print(bot_pos)
        return bot_pos, frames_grid
    else:
        print("No valid path found to target cell")
        return False

def refine_quadrants(quadrant_cells, n):
    if not quadrant_cells:
        print("No cells to refine in the quadrant.")
        return {}
    
    avg_row = sum(i for i, j in quadrant_cells) / len(quadrant_cells)
    avg_col = sum(j for i, j in quadrant_cells) / len(quadrant_cells)
    
    refined_quadrants = {
        'Q1': [],
        'Q2': [],
        'Q3': [],
        'Q4': []
    }

    for cell in quadrant_cells:
        i, j = cell
        if i < avg_row and j < avg_col:
            refined_quadrants['Q1'].append(cell)
        elif i < avg_row and j >= avg_col:
            refined_quadrants['Q2'].append(cell)
        elif i >= avg_row and j < avg_col:
            refined_quadrants['Q3'].append(cell)
        else:
            refined_quadrants['Q4'].append(cell)
    
    refined_quadrants = {k: v for k, v in refined_quadrants.items() if v}
    
    print(f"Refined Quadrants: {list(refined_quadrants.keys())}")
    return refined_quadrants

def main_improved(grid, n, bot_pos, rat_pos, alpha):
    frames_grid = []
    grid_for_map = np.copy(grid)
    frames_grid.append(np.copy(grid_for_map))
    grid_for_prob = np.zeros_like(grid, dtype=float)
    init_kb = list_possible_cells(grid_for_map, n)
    prob_grid = init_prob_cells(grid_for_prob, n, init_kb)
    quadrants = partition_grid(grid_for_map, n)
    t=0
    current_quadrant = None
    while t<10:
        hear_prob_rat = prob_ping_rat(bot_pos, rat_pos, alpha)
        print(hear_prob_rat)
        quadrant_probabilities = update_probabilities(prob_grid, quadrants, alpha, hear_prob_rat, bot_pos)
        for q, cell in quadrant_probabilities.items():
            print(f"{q}: {cell}")

        print("The probabilities are:")
        for q, cell in quadrants.items():
            print(f"{q}: {cell}")
        
        target_quadrant = max(quadrant_probabilities, key=quadrant_probabilities.get)
        print(f"The target quadrant is:\n {target_quadrant}")
        target_cell = weighted_center(target_quadrant, quadrants, prob_grid)
        print(f"Weighted center of {target_quadrant}: {target_cell}")

    #     if target_cell and 0 <= target_cell[0] < n and 0 <= target_cell[1] < n and grid_for_map[target_cell[0]][target_cell[1]] != -1:
    #         if target_quadrant==current_quadrant:
    #             print("Consistency")
    #             bot_pos, frames_grid = movement(grid_for_map, target_cell, bot_pos, n, frames_grid)
    #             refined_quadrants = refine_quadrants(quadrants[target_quadrant], n)
    #             if refined_quadrants:
    #                 del quadrants[target_quadrant]
    #                 for sub_quad, cells in refined_quadrants.items():
    #                     quadrants[sub_quad] = cells
    #                 print(f"Refined {target_quadrant} into {list(refined_quadrants.keys())}")
    #             else:
    #                 print(f"No sub-quadrants to refine in {target_quadrant}")
    #         else:
    #             print("Else ran")
    #             bot_pos, frames_grid = movement(grid_for_map, target_cell, bot_pos, n, frames_grid)
    #             current_max_quad = target_quadrant
    #     else:
    #         print(f"Invalid target cell selected: {target_cell}")
    #         print(grid_for_map[target_cell[0]][target_cell[1]])

    #     # bot_pos = new_bot_pos if 'new_bot_pos' in locals() else bot_pos

    #     if bot_pos==rat_pos:
    #         print("Bot has caught the rat!")
    #         frames_grid.append(np.copy(grid_for_map))
    #         break

        t+=1
    visualize_simulation_1(frames_grid)