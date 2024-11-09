import env_utils

#Generating a list of open_cells
def list_open_cells(grid, n):
    open_list = []
    for i in range(n):
        for j in range(n):
            if grid[i][j] == 0:
                open_list.append((i,j))
    return open_list

def sensing_neighbours_blocked(grid, bot_pos):
    cardinality = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    blocked_cells = 0
    for ci, cj in cardinality:
        test_i, test_j = bot_pos[0]+ci, bot_pos[1]+cj
        if grid[test_i][test_j] == 1:
            blocked_cells += 1
    # Debug output
    print(f"Sensing blocked neighbors at {bot_pos}: {blocked_cells} blocked")
    return blocked_cells

def update_kb_blocked(bot_kb, blocked, grid):
    new_bot_kb = []
    eliminated_cells = []  # Track cells that are eliminated
    for i in bot_kb:
        blocked_cells = sensing_neighbours_blocked(grid, (i[0], i[1]))
        if blocked_cells == blocked:
            new_bot_kb.append(i)
        else:
            eliminated_cells.append(i)
    # Debug output
    print(f"After sensing, possible locations: {len(new_bot_kb)}, eliminated: {len(eliminated_cells)}")
    return new_bot_kb


def check_common_direction(bot_kb, grid, last_move_direction):
    directions = {
        'north': 0,
        'south': 0,
        'east': 0,
        'west': 0
    }
    direction_offset = {
        'north':(-1,0),
        'south':(1,0),
        'east':(0,1),
        'west':(0,-1)      
    }
    opposite_direction = {
        'north': 'south',
        'south': 'north',
        'east': 'west',
        'west': 'east'
    }
    for i in bot_kb:
        for dir_name, (ci, cj) in direction_offset.items():
            test_i, test_j = i[0]+ci , i[1]+cj
            if grid[test_i][test_j]==0:
                directions[dir_name]+=1
    if last_move_direction:
        forbidden_dir = opposite_direction[last_move_direction]
        if len([d for d in directions if directions[d]>0])>1:
            directions[forbidden_dir] = -1 # so that it doen't come in max
    return max(directions, key=directions.get)

def attempt_movement(dir_check, grid, bot_pos):
    direction_offset = {
        'north': (-1, 0),
        'south': (1, 0),
        'east': (0, 1),
        'west': (0, -1)
    }
    move = direction_offset[dir_check]
    test_i, test_j = bot_pos[0] + move[0], bot_pos[1] + move[1]
    
    # Check if movement is possible
    if grid[test_i][test_j] == 1:
        print(f"Blocked movement in direction {dir_check} from {bot_pos}")
        return False, bot_pos  # Blocked
    else:
        # Move successfully
        grid[bot_pos[0]][bot_pos[1]] = 0
        bot_pos = (test_i, test_j)
        print(f"Successful movement to {bot_pos} in direction {dir_check}")
        grid[test_i][test_j] = 4  # Mark bot position on grid
        return True, bot_pos

    
def update_kb_movement(move_check, dir_check, bot_kb, grid):
    updated_kb_moves = []
    direction_offset = {
        'north':(-1,0),
        'south':(1,0),
        'east':(0,1),
        'west':(0,-1)      
    }
    direction = direction_offset[dir_check]
    for i in bot_kb:
        test_i, test_j = i[0] + direction[0], i[1] + direction[1]
        movement_possible = (grid[test_i][test_j] != 1)
        if move_check:
            if movement_possible:
                updated_kb_moves.append((test_i, test_j))
        else:
            if not movement_possible:
                updated_kb_moves.append(i)
    return updated_kb_moves

def main_function_2(grid, n, bot_pos):
    print(f"Original bot position (known to simulation): {bot_pos}")
    open_list = list_open_cells(grid, n)
    t = 0
    last_move_direction = None
    bot_kb = open_list
    action_toggle = True  # Start with sensing on the first timestep
    
    while len(bot_kb) > 1:
        if action_toggle:  # Sensing step
            blocked = sensing_neighbours_blocked(grid, bot_pos) 
            bot_kb = update_kb_blocked(bot_kb, blocked, grid)
            print(f"Sensing: Possible locations after update: {len(bot_kb)}")
        else:  # Movement step
            dir_check = check_common_direction(bot_kb, grid, last_move_direction)
            print(f"Attempting movement in direction: {dir_check}")
            move_check, bot_pos = attempt_movement(dir_check, grid, bot_pos)
            bot_kb = update_kb_movement(move_check, dir_check, bot_kb, grid)
            print(f"Moving: Possible locations after update: {len(bot_kb)}")
            if move_check:
                last_move_direction = dir_check

        if len(bot_kb) == 0:
            print("Error: No possible positions remain in the knowledge base.")
            break
        
        action_toggle = not action_toggle  # Alternate actions
        t += 1

    if len(bot_kb) == 1:
        print(f"Bot position is identified: {bot_kb[0]}")
    print(f"Total timesteps taken: {t}")