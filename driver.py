# from environment_utils import *
from env_utils import *
import sys
import os
import numpy as np
import random
from Bot import *

n = 30

seed_value = random.randrange(1, 1000)
print(seed_value)
random.seed(seed_value)
np.random.seed(seed_value)

grid = grid_init(n)
bot_pos = bot_init(grid, n, 4)
rat_pos = rat_init(grid, n, 2)

frames_bot1 = []


print("Bot 1")
random.seed(seed_value)
np.random.seed(seed_value)
print(grid)
# main_function(grid, n, bot_pos)
main_function_2(grid, n, bot_pos)