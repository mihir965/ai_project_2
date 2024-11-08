import numpy as np
from typing import Dict, Tuple, List, Optional
import random

class SpaceRatBot(BaselineBot):
    def _init_(self, grid: List[List[int]], alpha: float = 0.1):
        super()._init_(grid)
        self.alpha = alpha
        self.rat_knowledge_base = None  # Will be initialized after localization
        self.actions_taken['rat_detector'] = 0
    
    def initialize_rat_knowledge_base(self):
        """Initialize uniform probability distribution over all open cells"""
        total_open_cells = sum(row.count(1) for row in self.grid)
        probability = 1.0 / total_open_cells
        self.rat_knowledge_base = np.zeros((D, D))
        for i in range(D):
            for j in range(D):
                if self.grid[i][j] == 1:
                    self.rat_knowledge_base[i][j] = probability

    def get_ping_probability(self, bot_pos: Tuple[int, int], rat_pos: Tuple[int, int]) -> float:
        """Calculate probability of ping based on Manhattan distance"""
        manhattan_dist = abs(bot_pos[0] - rat_pos[0]) + abs(bot_pos[1] - rat_pos[1])
        if manhattan_dist == 0:  # Same cell
            return 1.0
        return np.exp(-self.alpha * (manhattan_dist - 1))

    def update_knowledge_base_with_ping(self, bot_pos: Tuple[int, int], received_ping: bool):
        """Update rat probability distribution based on ping result using Bayes' rule"""
        new_knowledge_base = np.zeros_like(self.rat_knowledge_base)
        
        # For each possible rat position
        total_probability = 0
        for i in range(D):
            for j in range(D):
                if self.grid[i][j] == 1:
                    ping_prob = self.get_ping_probability(bot_pos, (i, j))
                    prior = self.rat_knowledge_base[i, j]
                    
                    # P(evidence|rat_pos) * P(rat_pos)
                    if received_ping:
                        likelihood = ping_prob
                    else:
                        likelihood = 1 - ping_prob
                    
                    new_probability = likelihood * prior
                    new_knowledge_base[i, j] = new_probability
                    total_probability += new_probability
        
        # Normalize probabilities
        if total_probability > 0:
            self.rat_knowledge_base = new_knowledge_base / total_probability

    def get_most_likely_rat_position(self) -> Tuple[int, int]:
        """Return the cell with highest probability of containing the rat"""
        max_prob_idx = np.argmax(self.rat_knowledge_base)
        return (max_prob_idx // D, max_prob_idx % D)

    def get_next_move_direction(self, current_pos: Tuple[int, int], 
                              target_pos: Tuple[int, int]) -> Tuple[int, int]:
        """Determine best direction to move towards target"""
        row_diff = target_pos[0] - current_pos[0]
        col_diff = target_pos[1] - current_pos[1]
        
        # Prefer vertical movement if further in that direction
        if abs(row_diff) > abs(col_diff):
            return (1 if row_diff > 0 else -1, 0)
        else:
            return (0, 1 if col_diff > 0 else -1)

    def catch_rat(self, true_rat_pos: Tuple[int, int], visualize: bool = False) -> Dict:
        """Execute Phase 2: Track and catch the space rat"""
        if not self.current_position:
            raise ValueError("Bot must be localized before catching rat")
        
        window = None
        canvas = None
        if visualize:
            window = tk.Tk()
            window.title("Space Rat Hunt")
            canvas = tk.Canvas(window, width=D * CELL_SIZE, height=D * CELL_SIZE)
            canvas.pack()

        self.initialize_rat_knowledge_base()
        current_pos = self.current_position
        iterations = 0
        max_iterations = D * D  # Reasonable maximum iterations

        while iterations < max_iterations:
            iterations += 1
            
            if visualize:
                self._update_visualization_with_rat(canvas, current_pos, true_rat_pos)
                window.update()
                time.sleep(0.1)

            # Use rat detector
            self.actions_taken['rat_detector'] += 1
            manhattan_dist = abs(current_pos[0] - true_rat_pos[0]) + abs(current_pos[1] - true_rat_pos[1])
            
            # Check if we've caught the rat
            if manhattan_dist == 0:
                if visualize:
                    window.destroy()
                return self.actions_taken

            # Get ping with appropriate probability
            ping_probability = self.get_ping_probability(current_pos, true_rat_pos)
            received_ping = random.random() < ping_probability
            
            # Update knowledge base based on ping result
            self.update_knowledge_base_with_ping(current_pos, received_ping)
            
            # Move towards most likely rat position
            target_pos = self.get_most_likely_rat_position()
            move_direction = self.get_next_move_direction(current_pos, target_pos)
            
            success, new_pos = self.attempt_move(move_direction, current_pos)
            self.actions_taken['movements'] += 1
            current_pos = new_pos

        if visualize:
            window.destroy()
        return self.actions_taken

    def _update_visualization_with_rat(self, canvas: tk.Canvas, 
                                     bot_position: Tuple[int, int],
                                     rat_position: Tuple[int, int]):
        """Update visualization to show bot, rat, and probability distribution"""
        canvas.delete("all")
        
        # Draw grid and probability distribution
        max_prob = np.max(self.rat_knowledge_base)
        for row in range(D):
            for col in range(D):
                x0, y0 = col * CELL_SIZE, row * CELL_SIZE
                x1, y1 = x0 + CELL_SIZE, y0 + CELL_SIZE
                
                if (row, col) == bot_position:
                    color = "red"
                elif (row, col) == rat_position:
                    color = "green"
                elif self.grid[row][col] == 0:
                    color = "black"
                else:
                    # Create heat map for probability distribution
                    intensity = int(self.rat_knowledge_base[row, col] / max_prob * 255)
                    color = f"#{intensity:02x}{intensity:02x}ff"
                
                canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="gray")
        
        # Add stats
        stats_text = (
            f"Movements: {self.actions_taken['movements']}\n"
            f"Detector uses: {self.actions_taken['rat_detector']}"
        )
        canvas.create_text(10, 10, anchor="nw", text=stats_text, fill="blue")

def demo_full_mission():
    # Create grid
    grid = create_test_grid()
    
    # Find valid positions for bot and rat
    open_cells = [(i, j) for i in range(1, D-1) for j in range(1, D-1) 
                  if grid[i][j] == 1]
    bot_start_pos = random.choice(open_cells)
    rat_pos = random.choice([pos for pos in open_cells if pos != bot_start_pos])
    
    # Create and run bot
    bot = SpaceRatBot(grid, alpha=0.1)
    
    print("Phase 1: Localization")
    bot_pos = bot.locate_position(bot_start_pos, visualize=True)
    
    print("\nPhase 2: Rat Hunt")
    results = bot.catch_rat(rat_pos, visualize=True)
    
    print("\nFinal Results:")
    print(f"Total movements: {results['movements']}")
    print(f"Total blocked cell sensing: {results['sense_blocked']}")
    print(f"Total rat detector uses: {results['rat_detector']}")

if _name_ == "_main_":
    demo_full_mission()