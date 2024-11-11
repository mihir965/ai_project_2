import env_utils

#Generating a list of open_cells
def list_open_cells(grid, n):
    open_list = []
    for i in range(n):
        for j in range(n):
            if grid[i][j] == 0 or grid[i][j]==3:
                open_list.append((i,j))
    return open_list

def sensing_neighbours_blocked(grid, bot_pos, n):
    cardinality = [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1, 1), (-1,-1)]
    blocked_cells = 0
    for ci, cj in cardinality:
        test_i, test_j = bot_pos[0]+ci, bot_pos[1]+cj
        if 0 <= test_i < n and 0 <= test_j < n:
            if grid[test_i][test_j]==-1:
                blocked_cells+=1
        else:
            blocked_cells+=1
    return blocked_cells

def update_kb_blocked(bot_kb, blocked, grid, n):
    new_bot_kb = []
    for i in bot_kb:
        blocked_cells = sensing_neighbours_blocked(grid, (i[0],i[1]), n)
        if blocked_cells==blocked:
            new_bot_kb.append(i)
    return new_bot_kb

def check_common_direction(bot_kb, grid, last_move_direction, n):
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
            if 0 <= test_i < n and 0 <= test_j < n:
                if grid[test_i][test_j]==0:
                    directions[dir_name]+=1
    if last_move_direction:
        forbidden_dir = opposite_direction[last_move_direction]
        if len([d for d in directions if directions[d]>0])>1:
            directions[forbidden_dir] = -1 # so that it doesn't come in max
    return max(directions, key=directions.get)

def attempt_movement(dir_check, grid, bot_pos, n):
    direction_offset = {
        'north':(-1,0),
        'south':(1,0),
        'east':(0,1),
        'west':(0,-1)      
    }
    move = direction_offset[dir_check]
    test_i, test_j = bot_pos[0]+move[0], bot_pos[1]+move[1]
    if not (0 <= test_i < n and 0 <= test_j < n):
        return False, bot_pos
    if grid[test_i][test_j] == 1:
        return False, bot_pos
    else:
        grid[bot_pos[0]][bot_pos[1]] = 0
        bot_pos = (test_i, test_j)
        if grid[test_i][test_j] == 2:
            print("The bot caught the rat!")
        grid[test_i][test_j] = 3
        return True, bot_pos 
    
def update_kb_movement(move_check, dir_check, bot_kb, grid, n):
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
        if 0 <= test_i < n and 0 <= test_j < n:
            movement_possible = (grid[test_i][test_j] != 1)
        else:
            movement_possible = False
        if move_check:
            if movement_possible:
                updated_kb_moves.append((test_i, test_j))
        else:
            if not movement_possible:
                updated_kb_moves.append(i)
    return updated_kb_moves
        
def main_function(grid, n, bot_pos):
    print(f"Original bot position that simulation knows: {bot_pos}")
    open_list = list_open_cells(grid, n)
    t = 0
    last_move_direction = None
    bot_kb = open_list
    print(len(bot_kb))
    blocked_check = True
    while len(bot_kb) > 1:
        if blocked_check:
            blocked = sensing_neighbours_blocked(grid, bot_pos, n) 
            bot_kb = update_kb_blocked(bot_kb, blocked, grid, n)
            print(f"Number of blocked cells: {blocked}")
            print(f"Length of kb: {len(bot_kb)}")
            print("End of blocked check")
            print(f"Knowldege base after block check:\n{bot_kb}")
        if not blocked_check:
            print("Checking in directions")
            dir_check = check_common_direction(bot_kb, grid, last_move_direction, n)
            print(f"The most common dir: {dir_check}")
            # We will also move the bot if possible
            move_check, bot_pos = attempt_movement(dir_check, grid, bot_pos, n)
            print(f"Movement in {dir_check} is {move_check}")
            print(f"New pos: {bot_pos}")
            bot_kb = update_kb_movement(move_check, dir_check, bot_kb, grid, n)
            print(f"New length of kb: {len(bot_kb)}")
            if move_check:
                last_move_direction = dir_check
            print(f"Knowldege base after direction check:\n{bot_kb}")
        if len(bot_kb) == 0:
            print("Error: No possible positions remain in the knowledge base.")
            break
        blocked_check = not blocked_check
        print(f"Before next time step: length kb: {len(bot_kb)}")
        t+=1
    if len(bot_kb)==1:
        print(f"Remaining KB: {bot_kb[0]}\n Bot Pos: {bot_pos}")
    print(t)
    return bot_kb[0]