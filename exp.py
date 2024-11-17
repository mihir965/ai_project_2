# Example 5x5 grid where 1 represents blocked cells, 0 represents open cells
# for the sake of simplicity, we have assumed that all inner cells are open in this example

grid = [
    [1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1]
]

# Step 1: Initializing the probability map - Initially, there would be an equal chance of all open cells containing the rat
# 9 open cells --> each has 1/9 probability = 0.111

initial_probs = [
    [None,   None,   None,   None,   None],
    [None,   0.111,  0.111,  0.111,  None],
    [None,   0.111,  0.111,  0.111,  None],
    [None,   0.111,  0.111,  0.111,  None],
    [None,   None,   None,   None,   None]
]

# Assuming bot is at cell (1,1)

# Assuming α = 0.1

# In order to use the ping probability function, we first calculate the manhattan distance between the bot and each cell (represented as d(i, j))
# Manhattan distances from (1,1):
distances = [
    [None,   None,   None,   None,   None],
    [None,   0,      1,      2,      None],
    [None,   1,      2,      3,      None],
    [None,   2,      3,      4,      None],
    [None,   None,   None,   None,   None]
]
 
# Probability of ping at each distance with α = 0.1 (using prob formula, ping_probs = e^(-α(d(i, j) - 1)))
ping_probs = [
    [None,   None,   None,    None,   None],
    [None,   1.000,  0.905,   0.819,  None],
    [None,   0.905,  0.819,   0.741,  None],
    [None,   0.819,  0.741,   0.670,  None],
    [None,   None,   None,    None,   None]
]

# After this, there are 2 cases. Case 1 is when a ping is heard and Case 2 when no ping is heard

# CASE 1
'''
If we get a ping:
For each cell, multiply current probability by P(ping_probs)
Example: Cell at (1,2) had 0.111 initially
P(ping_probs) at distance 1 is 0.905
New probability = 0.111 * 0.905 = 0.100)

After a ping: Probabilities become higher for cells closer to the bot
''' 
unnorm_probs_after_ping = [
    [None,   None,   None,    None,   None],
    [None,   0.111,  0.100,   0.091,  None],
    [None,   0.100,  0.091,   0.082,  None],
    [None,   0.091,  0.082,   0.074,  None],
    [None,   None,   None,    None,   None]
]

# Normalized probabilities after ping:
norm_probs_after_ping = [
    [None,   None,   None,    None,   None],
    [None,   0.152,  0.137,   0.124,  None],
    [None,   0.137,  0.124,   0.112,  None],
    [None,   0.124,  0.112,   0.101,  None],
    [None,   None,   None,    None,   None]
]

# CASE 2
'''
If we DON'T get a ping:
For each cell, multiply by (1 - P(ping_probs))
Example: Cell at (1,2) had 0.111 initially
P(no ping) at distance 1 is (1 - 0.905) = 0.095
New probability = 0.111 * 0.095 = 0.011

After no ping: Probabilities become higher for cells farther from the bot
'''
unnorm_probs_after_no_ping = [
    [None,   None,   None,    None,   None],
    [None,   0.000,  0.011,   0.020,  None],
    [None,   0.011,  0.020,   0.029,  None],
    [None,   0.020,  0.029,   0.037,  None],
    [None,   None,   None,    None,   None]
]

# Normalized probabilities after no ping:
norm_probs_after_no_ping = [
    [None,   None,   None,    None,   None],
    [None,   0.000,  0.062,   0.113,  None],
    [None,   0.062,  0.113,   0.164,  None],
    [None,   0.113,  0.164,   0.209,  None],
    [None,   None,   None,    None,   None]
]

