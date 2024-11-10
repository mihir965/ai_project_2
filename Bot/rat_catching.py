from env_utils import *
from Bot.bot_movement import *
import math
import random
import numpy as np

# The rat can only occupy an open cell
def list_possible_cells(grid, n):
    possible_cells = []
    for i in range(n):
        for j in range(n):
            #0 = open 2 = Rat 4 = Bot
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
    # print(prob)
    # print(rand_chance)
    if prob>=rand_chance:
        return True
    else:
        return False
    
def prob_ping_j(bot_pos, j, alpha):
    dist = manhattan_dist(bot_pos, j)
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
    grid_for_map = grid
    grid_for_prob = np.array(grid, dtype=float)
    # init_kb_og = list_possible_cells(grid, n)
    init_kb = list_possible_cells(grid_for_prob, n)
    # print(f"Original grid poss:\n{init_kb_og}\nNP Grid poss:\n{init_kb_new}\nLengths: {len(init_kb_og)}\n{len(init_kb_new)}")
    #Redistribute intial probabilites
    prob_grid = init_prob_cells(grid_for_prob, n, init_kb)
    switch = True
    t = 0
    while True:
        if switch:
            #Use Rat detector to hear ping
            hear_prob_from_rat = prob_ping_rat(bot_pos, rat_pos, alpha)

            #Update the probabilites based on whether or not the ping was heard
            prob_grid = update_cells(prob_grid, init_kb, hear_prob_from_rat, bot_pos, alpha)

            #Get the cell with max probability
            max_prob = np.max(prob_grid)
            result = np.where(prob_grid==max_prob)
            max_cells = list(zip(result[0], result[1]))
            max_cells = [(int(row), int(col)) for row, col in max_cells]
            if max_prob==1:
                print(f"the rat was found at cell:{max_cells[0]}")

        if not switch:
            print(max_cells)
            path = plan_path_bot2(grid, bot_pos, max_cells[0], n)
            grid[bot_pos[0]][bot_pos[1]] = 0
            if len(path)==1:
                print("Broke by error")
                break
            bot_pos = path.pop(1)
            grid[bot_pos[0]][bot_pos[1]] = 1
            frames_grid.append(np.copy(grid))
        t+=1
        switch = not switch

        if bot_pos==rat_pos:
            print("Correct break")
            break
    visualize_simulation_1(frames_grid)
       
    








    # while True:
    #     print(f"Bot pos: {bot_pos}")
    #     print(f"Rat_pos: {rat_pos}")
    #     grid_2 = np.array(grid, dtype=float)
    #     list_poss_cells = list_possible_cells(grid_2, n)
    #     print(list_poss_cells)
    #     hear_prob=prob_ping_rat(bot_pos, rat_pos, alpha)
    #     print(hear_prob)
    #     #initialize the probabilities
    #     prob_grid = init_prob_cells(grid_2, n, list_poss_cells)
    #     kb = list_poss_cells
    #     prob_grid = update_cells(prob_grid, kb, hear_prob, bot_pos, alpha)
    #     max_prob = np.max(prob_grid)
    #     print(max_prob)
    #     result = np.where(prob_grid==max_prob)
    #     max_cells = list(zip(result[0], result[1]))
    #     max_cells = [(int(row), int(col)) for row, col in max_cells]
    #     print(max_cells[0])
    #     break
    # visualize_simulation_1(frames1)