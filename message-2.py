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
    current_quadrant = None

    while True:
        # Move the rat
        old_rat_pos = rat_pos
        rat_pos = simulate_rat_movement(grid, rat_pos)
        print(f"Step {t}: Rat moved from {old_rat_pos} to {rat_pos}")

        frames_grid.append(np.copy(grid))


        # Update probabilities based on sensor and rat movement
        hear_prob = prob_ping_rat(bot_pos, rat_pos, alpha)
        quadrant_probabilities, prob_grid = update_probabilities(
            prob_grid, quadrants, alpha, hear_prob, bot_pos, grid
        )

        # # Move the bot
        # if bot_pos != rat_pos:
        #     bot_pos, frames_grid, t = movement(grid, target_cell, bot_pos, n, frames_grid, rat_pos, t)
        #     print(f"Bot moved to {bot_pos}")
        # frames_grid.append(np.copy(grid))

        # Determine target quadrant and weighted center
        target_quadrant = max(quadrant_probabilities, key=quadrant_probabilities.get)
        print(f"The target quadrant is: {target_quadrant}")
        target_cell = weighted_center(target_quadrant, quadrants, prob_grid, grid_for_map, n)
        print(f"Weighted center of {target_quadrant}: {target_cell}")

        # Check if the target cell is valid
        if target_cell and 0 <= target_cell[0] < n and 0 <= target_cell[1] < n and grid_for_map[target_cell[0]][target_cell[1]] != -1:
            if current_quadrant == target_quadrant:
                print("Consistency within the same quadrant.")
                if bot_pos == target_cell:
                    print("Bot already at the target cell.")
                    continue
                # Move the bot to the target cell
                bot_pos, frames_grid, t = movement(grid_for_map, target_cell, bot_pos, n, frames_grid, rat_pos, t)
                # Refine the target quadrant
                refined_quadrants = refine_quadrants(target_quadrant, quadrants[target_quadrant], n)
                if refined_quadrants:
                    del quadrants[target_quadrant]
                    quadrants.update(refined_quadrants)
                    print(f"Refined {target_quadrant} into {list(refined_quadrants.keys())}")
            else:
                print("Switching to a new quadrant.")
                if bot_pos == target_cell:
                    print("Bot already at the target cell.")
                    continue
                bot_pos, frames_grid, t = movement(grid_for_map, target_cell, bot_pos, n, frames_grid, rat_pos, t)
                if bot_pos is False:
                    print("Bot movement failed.")
                    break
                current_quadrant = target_quadrant
        else:
            print(f"Invalid target cell selected: {target_cell}")
            print(grid_for_map[target_cell[0]][target_cell[1]])

        # Check if bot catches the rat
        if bot_pos == rat_pos:
            print(f"Bot caught the rat at {bot_pos} in {t} steps!")
            frames_grid.append(np.copy(grid_for_map))  # Final grid
            return True, frames_grid

        # Timeout condition
        if t > 1000:
            print("Timeout: Bot took too long.")
            return False, frames_grid

        t += 1