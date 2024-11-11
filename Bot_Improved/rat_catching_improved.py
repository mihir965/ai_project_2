from env_utils import *
from bot_movement import *
import math
import random
import numpy as np

#The rat can only occupy an open cell
def list_possible_cells(grid, n):
    possible_cells = []
    for i in range(n):
        for j in range(n):
            #0 = open 2 = Rat 3 = Bot
            if grid[i][j] == 0 or grid[i][j]==2:
                possible_cells.append((i, j))
    return possible_cells

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

#We will partition the grid into 4 quadrants
def partition_grid(grid, n):
    mid_row = n//2
    mid_col = n//2

    quad_1 = grid[:mid_row, :mid_col]
    quad_2 = grid[:mid_row, mid_col:]
    quad_3 = grid[mid_row:, :mid_col]
    quad_4 = grid[:mid_row, mid_col:]

    return (quad_1, quad_2, quad_3, quad_4)

def calc_quad_probs(q1, q2, q3, q4, n):
    for i in range(n):
        for j in range(n):
            



def main_improved(grid, n, bot_pos, rat_pos):
    q1, q2, q3, q4 = partition_grid(grid, n)
    