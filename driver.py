# from environment_utils import *
from env_utils import *
from bot_movement import *
import sys
import os
import numpy as np
import random
from Bot import *
from Bot_Improved import *

n = 30
# alpha = random.uniform(0.02, 0.2)
alpha = 0.1
print(alpha)

# seed_value = random.randrange(1, 1000)
seed_value = 808
print(seed_value)
random.seed(seed_value)
np.random.seed(seed_value)

grid = grid_init(n)
bot_pos = bot_init(grid, n, 3)
rat_pos = rat_init(grid, n, 2)

frames_bot1 = []


print("Bot 1")
random.seed(seed_value)
np.random.seed(seed_value)
# print(grid)
bot_pos = main_function(grid, n, bot_pos)
# rat_caught, frames = main_function_catching(grid, n, bot_pos, rat_pos, alpha)
# if rat_caught:
#     visualize_simulation_1(frames)
# frames = []
# rat_caught, frames = main_function_catching_moving_rat(grid, n, bot_pos, rat_pos, alpha)
# if rat_caught:
#     visualize_simulation_1(frames)

main_improved(grid, n, bot_pos, rat_pos, alpha)