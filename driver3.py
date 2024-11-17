from env_utils import *
from bot_movement import *
import sys
import os
import numpy as np
import random
from Bot import *
from Bot_Improved import *
import csv
from collections import defaultdict

n = 30

def initialize_comparison_log():
    with open("comparison_log.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Simulation Number", "Seed Value", "Alpha", "Baseline Outcome", "Improved Outcome"])

def run_single_comparison(alpha, simulation_num):
    # Generate a random seed for this simulation
    seed_value = random.randint(1, 1000)
    print(f"Alpha: {alpha:.2f}, Simulation: {simulation_num}, Seed: {seed_value}")
    random.seed(seed_value)
    np.random.seed(seed_value)
    
    # Initialize the grid and bot/rat positions
    grid = grid_init(n)
    bot_pos_baseline = bot_init(grid, n, 3)
    bot_pos_improved = bot_pos_baseline  # Both bots start in the same position
    rat_pos = rat_init(grid, n, 2)
    
    # Run the baseline bot
    baseline_caught = main_function_catching(grid, n, bot_pos_baseline, rat_pos, alpha, simulation_num, seed_value, True)
    
    # Reset the environment for the improved bot using the same seed
    random.seed(seed_value)
    np.random.seed(seed_value)
    grid = grid_init(n)
    bot_pos_improved = bot_init(grid, n, 3)
    rat_pos = rat_init(grid, n, 2)
    
    # Run the improved bot
    improved_caught = main_improved(grid, n, bot_pos_improved, rat_pos, alpha, simulation_num, seed_value)
    
    # Log the results
    with open("comparison_log.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([simulation_num, seed_value, f"{alpha:.2f}", "Success" if baseline_caught else "Failure", "Success" if improved_caught else "Failure"])
    
    return baseline_caught, improved_caught

def run_comparisons(alpha_start=0.0, alpha_end=0.2, alpha_step=0.05, simulations=50):

    initialize_comparison_log()  # Prepare the comparison log file
    
    # Generate alpha values from start to end with the given step size
    alpha_values = np.arange(alpha_start, alpha_end + alpha_step, alpha_step)
    
    # Track results for each bot
    baseline_success = defaultdict(int)
    improved_success = defaultdict(int)
    total_simulations = defaultdict(int)
    
    for alpha in alpha_values:
        for sim_num in range(1, simulations + 1):
            # Run a single comparison for both bots
            baseline_caught, improved_caught = run_single_comparison(alpha, sim_num)
            baseline_success[alpha] += int(baseline_caught)
            improved_success[alpha] += int(improved_caught)
            total_simulations[alpha] += 1
    
    # Calculate and print average accuracies
    print("\nAverage Accuracies per Alpha Value:")
    with open("comparison_log.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([])
        writer.writerow(["Alpha", "Baseline Accuracy", "Improved Accuracy"])
        for alpha in sorted(total_simulations.keys()):
            baseline_acc = baseline_success[alpha] / total_simulations[alpha]
            improved_acc = improved_success[alpha] / total_simulations[alpha]
            print(f"Alpha: {alpha:.2f} | Baseline: {baseline_acc:.2%} | Improved: {improved_acc:.2%}")
            writer.writerow([f"{alpha:.2f}", f"{baseline_acc:.2%}", f"{improved_acc:.2%}"])

if __name__ == "__main__":
    # Start the simulation across multiple values of alpha
    run_comparisons()
