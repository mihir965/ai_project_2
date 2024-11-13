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
