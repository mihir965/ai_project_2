# Suppose Q4 is the target quadrant, now split into Q4a and Q4b
def refine_quadrant(quadrant_cells, n):
    refined_quadrants = {
        'Q4a': [],
        'Q4b': [],
        'Q4c': [],
        'Q4d': []
    }
    
    mid_row = max(i for i, j in quadrant_cells) // 2
    mid_col = max(j for i, j in quadrant_cells) // 2
    
    for cell in quadrant_cells:
        i, j = cell
        if i < mid_row and j < mid_col:
            refined_quadrants['Q4a'].append(cell)
        elif i < mid_row and j >= mid_col:
            refined_quadrants['Q4b'].append(cell)
        elif i >= mid_row and j < mid_col:
            refined_quadrants['Q4c'].append(cell)
        else:
            refined_quadrants['Q4d'].append(cell)
    
    return refined_quadrants



# def main_improved(grid, n, bot_pos, rat_pos, alpha):
#     frames_grid = []
#     grid_for_map = np.copy(grid)
#     # print(grid_for_map)
#     frames_grid.append(np.copy(grid_for_map))
#     grid_for_prob = np.zeros_like(grid, dtype=float)
#     init_kb = list_possible_cells(grid_for_map, n)
#     prob_grid = init_prob_cells(grid_for_prob, n, init_kb)
#     prob_grid_dict = partition_grid(grid_for_map, n)
#     # print(prob_grid)
#     switch = True
#     t = 0
#     current_max_quad = 1
#     while t<5:
#         hear_prob_from_rat = prob_ping_rat(bot_pos, rat_pos, alpha)
#         print(hear_prob_from_rat)
#         quadrant_probabilities = update_probabilities(prob_grid, prob_grid_dict, alpha, hear_prob_from_rat, bot_pos, grid_for_map)
#         high_quadrants = {q: p for q, p in quadrant_probabilities.items()}

#         if high_quadrants:
#             target_quadrant = max(high_quadrants, key=high_quadrants.get)
#             print(f"Target quadrant: {target_quadrant}")

#             target_cell = weighted_center(target_quadrant, prob_grid_dict, prob_grid)
#             print(f"Weighted center of selected quadrant: {target_cell}")

#             if 0 <= target_cell[0] < n and 0 <= target_cell[1] < n and grid_for_map[target_cell[0]][target_cell[1]] != -1:
#                 if t%2!=0:
#                     if target_quadrant == current_max_quad:
#                         bot_pos, frames_grid = movement(grid_for_map, target_cell, bot_pos, n, frames_grid)
#                         sub_quadrants = refine_quadrants(prob_grid_dict[target_quadrant], n)
#                         prob_grid_dict = sub_quadrants
#                 else:
#                     bot_pos, frames_grid = movement(grid_for_map, target_cell, bot_pos, n, frames_grid)
#                     current_max_quad = target_quadrant
#         t+=1

#         if bot_pos==rat_pos:
#             print("Bot has caught the rat!")
#             frames_grid.append(np.copy(grid_for_map))
#             break
#     print(f"Total steps taken: {t}")
#     visualize_simulation_1(frames_grid)
