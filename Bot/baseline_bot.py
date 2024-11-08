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
    cardinality = [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1, 1), (-1,-1)]
    blocked_cells = 0
    for ci, cj in cardinality:
        test_i, test_j = bot_pos[0]+ci, bot_pos[1]+cj
        if grid[test_i][test_j]==1:
            blocked_cells+=1
    return blocked_cells

def update_kb_blocked(bot_kb, blocked, grid):
    new_bot_kb = []
    cardinality = [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1, 1), (-1,-1)]
    for i in bot_kb:
        blocked_cells = sensing_neighbours_blocked(grid, (i[0],i[1]))
        if blocked_cells==blocked:
            new_bot_kb.append(i)
    return new_bot_kb


def check_common_direction(bot_kb, grid):
    directions = {
        'north': 0,
        'south': 0,
        'east': 0,
        'west': 0
    }
    cardinality = [(0,1), (0,-1), (1,0), (-1,0)]
    for i in bot_kb:
        for ci, cj in cardinality:
            test_i, test_j = i[0]+ci, i[1]+cj
            if grid[test_i][test_j]==0 and (ci, cj)==(0,1):
                directions['east']+=1
            elif grid[test_i][test_j]==0 and (ci, cj)==(0,-1):
                directions['west']+=1
            elif grid[test_i][test_j]==0 and (ci, cj)==(1,0):
                directions['south']+=1
            elif grid[test_i][test_j]==0 and (ci, cj)==(-1,0):
                directions['north']+=1
    return max(directions, key=directions.get)

def attempt_movement(dir_check, grid, bot_pos):
    if dir_check == 'east':
        move = (0,1)
        test_i, test_j = bot_pos[0]+move[0], bot_pos[1]+move[1]
        if grid[test_i][test_j]==1:
            return False
        elif grid[test_i][test_j]==0:
            return True
        elif grid[test_i][test_j]==2:
            print("The bot caught the rat!")
            return True
    if dir_check == 'west':
        move = (0,-1)
        test_i, test_j = bot_pos[0]+move[0], bot_pos[1]+move[1]
        if grid[test_i][test_j]==1:
            return False
        elif grid[test_i][test_j]==0:
            return True
        elif grid[test_i][test_j]==2:
            print("The bot caught the rat!")
            return True
    if dir_check == 'south':
        move = (1,0)
        test_i, test_j = bot_pos[0]+move[0], bot_pos[1]+move[1]
        if grid[test_i][test_j]==1:
            return False
        elif grid[test_i][test_j]==0:
            return True
        elif grid[test_i][test_j]==2:
            print("The bot caught the rat!")
            return True
    if dir_check == 'north':
        move = (-1,0)
        test_i, test_j = bot_pos[0]+move[0], bot_pos[1]+move[1]
        if grid[test_i][test_j]==1:
            return False
        elif grid[test_i][test_j]==0:
            return True
        elif grid[test_i][test_j]==2:
            print("The bot caught the rat!")
            return True
    
def update_kb_movement(move_check, bot_kb):
    if move_check==True

def main_function(grid, n, bot_pos):
    open_list = list_open_cells(grid, n)
    blocked = sensing_neighbours_blocked(grid, bot_pos)
    # print(blocked)
    # print(len(open_list))
    bot_kb = open_list
    bot_kb = update_kb_blocked(bot_kb, blocked, grid)
    # print(len(bot_kb))
    dir_check = check_common_direction(bot_kb, grid)
    print(dir_check)
    move_check = attempt_movement(dir_check, grid, bot_pos)
    # print(boo)
