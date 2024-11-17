from env_utils import *
from bot_movement import *
import math
import random
import numpy as np

def log_simulation_result(simulation_num, seed, alpha, outcome):
    with open("simulation_log.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([simulation_num, seed, f"{alpha:.2f}", outcome])

def list_possible_cells(grid, n):
    possible_cells = []
    for i in range(n):
        for j in range(n):
            #0 = open 2 = Rat 4 = Bot
            if grid[i][j] == 0 or grid[i][j] == 2:
                possible_cells.append((i, j))
    return possible_cells

def get_valid_rat_moves(grid, rat_pos):
    n = len(grid)
    possible_moves = []
    directions = [(-1,0), (0,1), (1,0), (0,-1)]
    
    for dx, dy in directions:
        new_x, new_y = rat_pos[0] + dx, rat_pos[1] + dy
        if (is_valid(new_x, new_y, n) and 
            is_unblocked(grid, new_x, new_y)):
            possible_moves.append((new_x, new_y))
    
    # Include current position as rat might stay
    possible_moves.append(rat_pos)
    return possible_moves

def manhattan_dist(bot_pos, j):
    return abs(bot_pos[0] - j[0]) + abs(bot_pos[1] - j[1])

def prob_ping_rat(bot_pos, rat_pos, alpha):
    dist = manhattan_dist(bot_pos, rat_pos)
    exponent = -1*(alpha*(dist-1))
    prob = math.exp(exponent)
    rand_chance = random.uniform(0.0, 1.0)
    return prob >= rand_chance

def prob_ping_j(bot_pos, j, alpha):
    dist = manhattan_dist(bot_pos, j)
    exponent = -1*(alpha*(dist-1))
    return math.exp(exponent)

def update_prob_after_movement(prob_grid, grid):
    #Update probability grid after rat movement using environment constraints
    n = len(prob_grid)
    new_prob_grid = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            if prob_grid[i][j] > 0:
                valid_moves = get_valid_rat_moves(grid, (i,j))
                # Distribute probability equally among possible next positions
                move_prob = prob_grid[i][j] / len(valid_moves)
                for move in valid_moves:
                    new_prob_grid[move[0]][move[1]] += move_prob
    
    return new_prob_grid

def update_cells_moving_rat(prob_grid, kb, hear_prob, bot_pos, alpha, grid):
    new_prob_grid = np.copy(prob_grid)
    total_prob_sensor = 0
    
    # First update based on sensor reading
    if hear_prob:
        for cell in kb:
            total_prob_sensor += prob_ping_j(bot_pos, cell, alpha) * new_prob_grid[cell[0]][cell[1]]
    else:
        for cell in kb:
            total_prob_sensor += (1-prob_ping_j(bot_pos, cell, alpha)) * new_prob_grid[cell[0]][cell[1]]
    
    if total_prob_sensor != 0:
        if hear_prob:
            for cell in kb:
                new_prob_grid[cell[0]][cell[1]] = (prob_ping_j(bot_pos, cell, alpha) * new_prob_grid[cell[0]][cell[1]]) / total_prob_sensor
        else:
            for cell in kb:
                new_prob_grid[cell[0]][cell[1]] = ((1-prob_ping_j(bot_pos, cell, alpha)) * new_prob_grid[cell[0]][cell[1]]) / total_prob_sensor
    
    # Then update based on possible rat movement
    new_prob_grid = update_prob_after_movement(new_prob_grid, grid)
    
    return new_prob_grid

def init_prob_cells(grid, n, list_poss_cells):
    new_grid = np.copy(grid)
    num_possible_cells = len(list_poss_cells)
    init_value = 1/num_possible_cells
    for cell in list_poss_cells:
        new_grid[cell[0]][cell[1]] = init_value
    return new_grid

def simulate_rat_movement(grid, rat_pos):
    valid_moves = get_valid_rat_moves(grid, rat_pos)
    new_pos = random.choice(valid_moves)
    if new_pos != rat_pos:
        grid[rat_pos[0]][rat_pos[1]] = 0
        grid[new_pos[0]][new_pos[1]] = 2
    return new_pos

def main_function_catching_moving_rat(grid, n, bot_pos, rat_pos, alpha, simulation_num, seed_value, driver_comparison):
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
            
            # Update probabilities considering both sensor reading and rat movement
            prob_grid = update_cells_moving_rat(prob_grid, init_kb, hear_prob_from_rat, bot_pos, alpha, grid)
            
            # Store probability heatmap frame
            frames_heatmap.append(np.copy(prob_grid))
            
            # Get cell with max probability
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
            if bot_pos==target_cell:
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
            path = plan_path_bot2(grid, bot_pos, max_cells[0], n)
            if path is None or len(path) <= 1:
                print("No path found to the target cell.")
                break  
            # Update bot position
            grid[bot_pos[0]][bot_pos[1]] = 0
            bot_pos = path[1]
            grid[bot_pos[0]][bot_pos[1]] = 3   
            rat_pos = simulate_rat_movement(grid, rat_pos)

        frames_grid.append(np.copy(grid))        
        t += 1
        switch = not switch

        if bot_pos == rat_pos:
            print(f"Probability at rat's position ({rat_pos}): {prob_grid[rat_pos[0]][rat_pos[1]]}")
            print("Bot has caught the rat")
            log_simulation_result(simulation_num, seed_value, alpha, "Success")
            print(f"Total steps taken: {t}")
            if not driver_comparison:
                visualize_simulation_1(frames_grid)
            return True
        
        if t > 2000:
            print(f"The bot is stuck or taking too long:")
            log_simulation_result(simulation_num, seed_value, alpha, "Failure")
            if not driver_comparison:
                visualize_simulation_1(frames_grid)
            return False
