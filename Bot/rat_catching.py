import env_utils

# The rat can only occupy an open cell
def list_possible_cells(grid, n):
    possible_cells = []
    for i in range(n):
        for j in range(n):
            if grid[i][j] == 0 or 2:
                possible_cells.append((i, j))
    return possible_cells