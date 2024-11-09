# Example 5x5 grid where 1 represents walls, 0 represents open cells
grid = [
    [1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1]
]

def print_probabilities(probs):
    """Print probability grid with 3 decimal places"""
    for row in probs:
        print([f'{p:.3f}' if p is not None else 'WALL ' for p in row])

# Step 1: Initial probabilities
# 9 open cells, so each has 1/9 probability
initial_probs = [
    [None,   None,   None,   None,   None],
    [None,   0.111,  0.111,  0.111,  None],
    [None,   0.111,  0.111,  0.111,  None],
    [None,   0.111,  0.111,  0.111,  None],
    [None,   None,   None,   None,   None]
]

# Assuming bot is at (1,1)

# with α = 0.1

# Manhattan distances from (1,1):
distances = [
    [None,   None,   None,   None,   None],
    [None,   0,      1,      2,      None],
    [None,   1,      2,      3,      None],
    [None,   2,      3,      4,      None],
    [None,   None,   None,   None,   None]
]
 
# Probability of ping at each distance with α = 0.1 (using prob formula)
ping_probs = [
    [None,   None,   None,    None,   None],
    [None,   1.000,  0.905,   0.819,  None],
    [None,   0.905,  0.819,   0.741,  None],
    [None,   0.819,  0.741,   0.670,  None],
    [None,   None,   None,    None,   None]
]

'''
if we get a ping ( For each cell, multiply current probability by P(ping)
Example: Cell at (1,2) had 0.111 initially
P(ping) at distance 1 is 0.905
New unnormalized probability = 0.111 * 0.905 = 0.100)

After a ping: Probabilities become higher for cells closer to the bot
''' 

# If we get a ping, new unnormalized probabilities:  
unnorm_probs_after_ping = [
    [None,   None,   None,    None,   None],
    [None,   0.111,  0.100,   0.091,  None],
    [None,   0.100,  0.091,   0.082,  None],
    [None,   0.091,  0.082,   0.074,  None],
    [None,   None,   None,    None,   None]
]

# # Normalized probabilities after ping:
# norm_probs_after_ping = [
#     [None,   None,   None,    None,   None],
#     [None,   0.152,  0.137,   0.124,  None],
#     [None,   0.137,  0.124,   0.112,  None],
#     [None,   0.124,  0.112,   0.101,  None],
#     [None,   None,   None,    None,   None]
# ]

'''
If we DON'T get a ping:
For each cell, multiply by (1 - P(ping))
Example: Cell at (1,2) had 0.111 initially
P(no ping) at distance 1 is (1 - 0.905) = 0.095
New unnormalized probability = 0.111 * 0.095 = 0.011

After no ping: Probabilities become higher for cells farther from the bot

'''

# If we don't get a ping, new unnormalized probabilities:
unnorm_probs_after_no_ping = [
    [None,   None,   None,    None,   None],
    [None,   0.000,  0.011,   0.020,  None],
    [None,   0.011,  0.020,   0.029,  None],
    [None,   0.020,  0.029,   0.037,  None],
    [None,   None,   None,    None,   None]
]

# # Normalized probabilities after no ping:
# norm_probs_after_no_ping = [
#     [None,   None,   None,    None,   None],
#     [None,   0.000,  0.062,   0.113,  None],
#     [None,   0.062,  0.113,   0.164,  None],
#     [None,   0.113,  0.164,   0.209,  None],
#     [None,   None,   None,    None,   None]
# ]


'''
The cell where the bot is becomes:

Zero probability after no ping (we know rat isn't there)
Highest probability after ping (most likely place if we hear ping)

'''