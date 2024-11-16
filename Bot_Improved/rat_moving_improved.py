from env_utils import *
from bot_movement import *
import math
import random
import numpy as np

# def log_simulation_result(simulation_num, seed, alpha, outcome):
#     with open("simulation_log.csv", mode="a", newline="") as file:
#         writer = csv.writer(file)
#         # Ensure all four values are written in the correct order
#         writer.writerow([simulation_num, seed, f"{alpha:.2f}", outcome])

#The rat can only occupy an open cell
def list_possible_cells(grid, n):
    possible_cells = []
    for i in range(n):
        for j in range(n):
            #0 = open 2 = Rat 3 = Bot
            if grid[i][j] == 0 or grid[i][j]==2:
                possible_cells.append((i, j))
    return possible_cells

def get_valid_rat_moves(grid, rat_pos):
    """Get all possible moves for the rat."""
    n = len(grid)
    possible_moves = []
    directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    
    for dx, dy in directions:
        new_x, new_y = rat_pos[0] + dx, rat_pos[1] + dy
        if (is_valid(new_x, new_y, n) and 
            is_unblocked(grid, new_x, new_y)):
            possible_moves.append((new_x, new_y))
    
    # Include current position as the rat might stay
    possible_moves.append(rat_pos)
    return possible_moves

def simulate_rat_movement(grid, rat_pos):
    """Move the rat to a random valid adjacent cell."""
    valid_moves = get_valid_rat_moves(grid, rat_pos)
    new_pos = random.choice(valid_moves)
    if new_pos != rat_pos:  # Only update grid if the rat moves
        grid[rat_pos[0]][rat_pos[1]] = 0  # Clear old position
        grid[new_pos[0]][new_pos[1]] = 2  # Set new position
    return new_pos

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

def update_probabilities(prob_grid, prob_grid_dict, alpha, hear_prob, bot_pos, grid):
    quadrant_probabilities = {quadrant: 0.0 for quadrant in prob_grid_dict.keys()}
    total_prob_sensor = 0.0
    new_prob_grid = np.copy(prob_grid)

    # Sensor-based probability updates (existing logic)
    if hear_prob:
        for quadrant, cells in prob_grid_dict.items():
            for cell in cells:
                total_prob_sensor += prob_ping_j(bot_pos, cell, alpha) * new_prob_grid[cell[0]][cell[1]]
    else:
        for quadrant, cells in prob_grid_dict.items():
            for cell in cells:
                total_prob_sensor += (1 - prob_ping_j(bot_pos, cell, alpha)) * new_prob_grid[cell[0]][cell[1]]

    if total_prob_sensor != 0:
        if hear_prob:
            for quadrant, cells in prob_grid_dict.items():
                for cell in cells:
                    p_ping_j_val = prob_ping_j(bot_pos, cell, alpha)
                    updated_p = (p_ping_j_val * new_prob_grid[cell[0]][cell[1]]) / total_prob_sensor
                    new_prob_grid[cell[0]][cell[1]] = updated_p
                    quadrant_probabilities[quadrant] += updated_p
        else:
            for quadrant, cells in prob_grid_dict.items():
                for cell in cells:
                    p_ping_j_val = (1 - prob_ping_j(bot_pos, cell, alpha))
                    updated_p = (p_ping_j_val * new_prob_grid[cell[0]][cell[1]]) / total_prob_sensor
                    new_prob_grid[cell[0]][cell[1]] = updated_p
                    quadrant_probabilities[quadrant] += updated_p

    # Normalize quadrant probabilities
    total_quadrant_prob = sum(quadrant_probabilities.values())
    if total_quadrant_prob > 0:
        for quadrant in quadrant_probabilities:
            quadrant_probabilities[quadrant] /= total_quadrant_prob

    # Update probabilities based on rat movement
    new_prob_grid = update_prob_after_movement(new_prob_grid, grid)

    return quadrant_probabilities, new_prob_grid


def update_prob_after_movement(prob_grid, grid):
    """Update probability grid after rat movement using environment constraints."""
    n = len(prob_grid)
    new_prob_grid = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            if prob_grid[i][j] > 0:
                valid_moves = get_valid_rat_moves(grid, (i, j))
                # Distribute probability equally among possible next positions
                move_prob = prob_grid[i][j] / len(valid_moves)
                for move in valid_moves:
                    new_prob_grid[move[0]][move[1]] += move_prob
    
    return new_prob_grid

# Probability update for moving rat
def update_cells_moving_rat(prob_grid, kb, hear_prob, bot_pos, alpha, grid):
    """Update probability grid to handle moving rat."""
    new_prob_grid = np.copy(prob_grid)
    total_prob_sensor = 0

    # Update based on sensor reading
    if hear_prob:
        for cell in kb:
            total_prob_sensor += prob_ping_j(bot_pos, cell, alpha) * new_prob_grid[cell[0]][cell[1]]
    else:
        for cell in kb:
            total_prob_sensor += (1 - prob_ping_j(bot_pos, cell, alpha)) * new_prob_grid[cell[0]][cell[1]]

    if total_prob_sensor != 0:
        if hear_prob:
            for cell in kb:
                new_prob_grid[cell[0]][cell[1]] = (prob_ping_j(bot_pos, cell, alpha) * new_prob_grid[cell[0]][cell[1]]) / total_prob_sensor
        else:
            for cell in kb:
                new_prob_grid[cell[0]][cell[1]] = ((1 - prob_ping_j(bot_pos, cell, alpha)) * new_prob_grid[cell[0]][cell[1]]) / total_prob_sensor

    # Update based on rat movement
    new_prob_grid = update_prob_after_movement(new_prob_grid, grid)
    return new_prob_grid

def weighted_center(target_quadrant, prob_grid_dict, prob_grid, grid_for_map, n):
    sum_x = 0.0
    sum_y = 0.0
    sum_p = 0.0

    for cell in prob_grid_dict[target_quadrant]:
        i, j = cell
        p = prob_grid[i][j]
        sum_x += p * i
        sum_y += p * j
        sum_p += p

    if sum_p > 0:
        x_c = sum_x/sum_p
        y_c = sum_y/sum_p
        x_final = int(round(x_c))
        y_final = int(round(y_c))
        if grid_for_map[x_final][y_final] == -1:
            print("invalid")
            cardinal_directions = [(0,1), (0,-1), (1,0), (-1,0)]
            for i, j in cardinal_directions:
                    while is_valid(x_final, y_final, n) and not is_unblocked(grid_for_map, x_final, y_final):
                        x_final, y_final = x_final+i, y_final+j
        target_cell = (x_final, y_final)
    else:
        target_cell = random.choice(prob_grid_dict[target_quadrant]) if prob_grid_dict[target_quadrant] else None

    return target_cell   

def movement(grid_for_map, target_cell, bot_pos, n, frames_grid, rat_pos, t):
    path = plan_path_bot2(grid_for_map, bot_pos, target_cell, n)
    if path and len(path)>1:
        halfway = len(path)//2
        # print(path)
        # print(f"Halfway is :{path[halfway]}")
        halfway_coordinates = path[halfway]
        # print(target_cell)
        # print(path[len(path)-1])
        # final_coordinates = path[len(path)-1]
        while True:
            t+=1
            # old_pos = bot_pos
            grid_for_map[bot_pos[0]][bot_pos[1]] = 0
            bot_pos = path.pop(1)
            grid_for_map[bot_pos[0]][bot_pos[1]] = 3
            # print(f"Moving bot from {old_pos} to {bot_pos}")
            if bot_pos==halfway_coordinates:
                break
            frames_grid.append(np.copy(grid_for_map))
            # print(bot_pos)
        # print(f"Moving bot from {old_pos} to {bot_pos}")
        frames_grid.append(np.copy(grid_for_map))
        # print(bot_pos)
        return bot_pos, frames_grid, t
    else:
        print(f"The position of the rat is {rat_pos}\nThe bot is at {bot_pos}")
        print(f"No valid path found to target cell: {target_cell}")
        return False, frames_grid, t

def refine_quadrants(parent_quadrant_name, quadrant_cells, n):
    print("Refine Quadrants ran")
    if not quadrant_cells:
        print("No cells to refine in the quadrant.")
        return {}
    
    avg_row = sum(i for i, j in quadrant_cells) / len(quadrant_cells)
    avg_col = sum(j for i, j in quadrant_cells) / len(quadrant_cells)
    
    refined_quadrants = {
        f"{parent_quadrant_name}_Q1": [],
        f"{parent_quadrant_name}_Q2": [],
        f"{parent_quadrant_name}_Q3": [],
        f"{parent_quadrant_name}_Q4": []
    }

    for cell in quadrant_cells:
        i, j = cell
        if i < avg_row and j < avg_col:
            refined_quadrants[f'{parent_quadrant_name}_Q1'].append(cell)
        elif i < avg_row and j >= avg_col:
            refined_quadrants[f'{parent_quadrant_name}_Q2'].append(cell)
        elif i >= avg_row and j < avg_col:
            refined_quadrants[f'{parent_quadrant_name}_Q3'].append(cell)
        else:
            refined_quadrants[f'{parent_quadrant_name}_Q4'].append(cell)
    
    refined_quadrants = {k: v for k, v in refined_quadrants.items() if v}
    
    print(f"Refined Quadrants: {list(refined_quadrants.keys())}")
    return refined_quadrants

def main_improved_with_moving_rat(grid, n, bot_pos, rat_pos, alpha):
    frames_grid = []  # Store grid frames for bot and rat visualization
    frames_heatmap = []  # Store probability heatmap frames
    grid_for_map = np.copy(grid)
    frames_grid.append(np.copy(grid_for_map))  # Initial grid
    grid_for_prob = np.zeros_like(grid, dtype=float)
    init_kb = list_possible_cells(grid_for_map, n)
    prob_grid = init_prob_cells(grid_for_prob, n, init_kb)
    frames_heatmap.append(np.copy(prob_grid))  # Initial heatmap
    quadrants = partition_grid(grid_for_map, n)
    t = 0

    while True:
        # Move the rat
        old_rat_pos = rat_pos
        rat_pos = simulate_rat_movement(grid, rat_pos)
        print(f"Step {t}: Rat moved from {old_rat_pos} to {rat_pos}")

        # Update probabilities based on sensor and rat movement
        hear_prob = prob_ping_rat(bot_pos, rat_pos, alpha)
        prob_grid = update_cells_moving_rat(prob_grid, init_kb, hear_prob, bot_pos, alpha, grid)
        frames_heatmap.append(np.copy(prob_grid))  # Append updated heatmap

        # Determine target cell with maximum probability
        max_prob = np.max(prob_grid)
        result = np.where(prob_grid == max_prob)
        max_cells = list(zip(result[0], result[1]))
        max_cells = [(int(row), int(col)) for row, col in max_cells]
        if not max_cells:
            print("No cells with probabilities found!")
            return False, frames_grid, frames_heatmap
        target_cell = max_cells[0]

        # Move bot toward the target cell
        if bot_pos == target_cell:
            print("Bot already at the target cell.")
        else:
            path = plan_path_bot2(grid, bot_pos, target_cell, n)
            if not path or len(path) <= 1:
                print("No valid path to target cell.")
                return False, frames_grid, frames_heatmap
            grid[bot_pos[0]][bot_pos[1]] = 0  # Clear old bot position
            bot_pos = path[1]  # Take the first step
            grid[bot_pos[0]][bot_pos[1]] = 3  # Update bot position
            frames_grid.append(np.copy(grid))  # Append updated grid

        print(f"Step {t}: Bot moved to {bot_pos}")

        # Check if bot catches the rat
        if bot_pos == rat_pos:
            print(f"Bot caught the rat at {bot_pos} in {t} steps!")
            frames_grid.append(np.copy(grid))  # Final grid
            return True, frames_grid

        # Timeout condition
        if t > 1000:
            print("Timeout: Bot took too long.")
            return False, frames_grid

        t += 1

