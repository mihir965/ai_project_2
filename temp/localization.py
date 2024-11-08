import tkinter as tk
import random
from typing import Set, Tuple, List, Optional
import time

# Define grid dimension and cell size
D = 30
CELL_SIZE = 20

class BaselineBot:
    def __init__(self, grid: List[List[int]]):
        self.grid = grid
        self.knowledge_base: Set[Tuple[int, int]] = self._initialize_knowledge_base()
        self.current_position: Optional[Tuple[int, int]] = None
        self.actions_taken = {
            'movements': 0,
            'sense_blocked': 0
        }
        self.max_iterations = 100  # Add maximum iterations limit
    
    def _initialize_knowledge_base(self) -> Set[Tuple[int, int]]:
        """Initialize knowledge base with all possible open positions"""
        return {(i, j) for i in range(1, D-1) for j in range(1, D-1) 
                if self.grid[i][j] == 1}
    
    def sense_blocked_neighbors(self, row: int, col: int) -> int:
        """Count blocked neighboring cells"""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), 
                     (-1, -1), (-1, 1), (1, -1), (1, 1)]
        count = 0
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < D and 0 <= new_col < D and 
                self.grid[new_row][new_col] == 0):
                count += 1
        return count
    
    def get_most_common_open_direction(self) -> Tuple[int, int]:
        """Identify direction that's most commonly open from possible positions"""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        direction_scores = {d: 0 for d in directions}
        
        for pos in self.knowledge_base:
            row, col = pos
            for d in directions:
                dr, dc = d
                new_row, new_col = row + dr, col + dc
                if (1 <= new_row < D-1 and 1 <= new_col < D-1 and 
                    self.grid[new_row][new_col] == 1):
                    direction_scores[d] += 1
        
        # Choose the direction with the highest score
        return max(directions, key=lambda d: direction_scores[d])
    
    def update_knowledge_base_after_sense(self, blocked_count: int):
        """Update knowledge base based on sensed blocked neighbors"""
        new_kb = set()
        for pos in self.knowledge_base:
            if self.sense_blocked_neighbors(*pos) == blocked_count:
                new_kb.add(pos)
        self.knowledge_base = new_kb
    
    def update_knowledge_base_after_move(self, direction: Tuple[int, int], 
                                       move_successful: bool):
        """Update knowledge base based on movement attempt result"""
        dr, dc = direction
        new_kb = set()
        
        for pos in self.knowledge_base:
            row, col = pos
            new_row, new_col = row + dr, col + dc
            can_move = (1 <= new_row < D-1 and 1 <= new_col < D-1 and 
                       self.grid[new_row][new_col] == 1)
            
            if move_successful and can_move:
                new_kb.add((new_row, new_col))
            elif not move_successful and not can_move:
                new_kb.add(pos)
        
        self.knowledge_base = new_kb
    
    def attempt_move(self, direction: Tuple[int, int], 
                    true_position: Tuple[int, int]) -> Tuple[bool, Tuple[int, int]]:
        """Attempt to move in given direction, return success and new position"""
        row, col = true_position
        dr, dc = direction
        new_row, new_col = row + dr, col + dc
        
        if (1 <= new_row < D-1 and 1 <= new_col < D-1 and 
            self.grid[new_row][new_col] == 1):
            return True, (new_row, new_col)
        return False, (row, col)
    
    def locate_position(self, true_position: Tuple[int, int], 
                       visualize: bool = False) -> Tuple[int, int]:
        """Execute Phase 1: Identify bot's position"""
        window = None
        canvas = None
        iteration_count = 0
        last_kb_size = len(self.knowledge_base)
        stuck_count = 0
        
        if visualize:
            window = tk.Tk()
            window.title("Bot Localization Process")
            canvas = tk.Canvas(window, width=D * CELL_SIZE, height=D * CELL_SIZE)
            canvas.pack()
        
        current_pos = true_position
        
        while len(self.knowledge_base) > 1 and iteration_count < self.max_iterations:
            iteration_count += 1
            
            if visualize:
                self._update_visualization(canvas, current_pos)
                window.update()
                time.sleep(0.1)
            
            # Sense phase
            blocked_count = self.sense_blocked_neighbors(*current_pos)
            self.actions_taken['sense_blocked'] += 1
            self.update_knowledge_base_after_sense(blocked_count)
            
            # Check if we've identified the position
            if len(self.knowledge_base) == 1:
                break
            
            # Move phase
            direction = self.get_most_common_open_direction()
            success, new_pos = self.attempt_move(direction, current_pos)
            self.actions_taken['movements'] += 1
            self.update_knowledge_base_after_move(direction, success)
            current_pos = new_pos
            
            # Check if we're stuck
            if len(self.knowledge_base) == last_kb_size:
                stuck_count += 1
            else:
                stuck_count = 0
                
            if stuck_count > 5:  # If stuck for too many iterations, break
                break
                
            last_kb_size = len(self.knowledge_base)
            
            # Safety check for empty knowledge base
            if not self.knowledge_base:
                print("Error: Knowledge base is empty!")
                break
        
        # Set final position
        if len(self.knowledge_base) == 1:
            self.current_position = list(self.knowledge_base)[0]
        else:
            # If we couldn't narrow down to one position, take the closest one
            self.current_position = min(self.knowledge_base, 
                key=lambda pos: abs(pos[0] - current_pos[0]) + abs(pos[1] - current_pos[1]))
        
        if visualize:
            self._update_visualization(canvas, current_pos)
            window.update()
            time.sleep(1)
            window.destroy()
        
        return self.current_position
    
    def _update_visualization(self, canvas: tk.Canvas, 
                            bot_position: Tuple[int, int]):
        """Update the visualization of the grid and knowledge base"""
        canvas.delete("all")
        
        for row in range(D):
            for col in range(D):
                x0, y0 = col * CELL_SIZE, row * CELL_SIZE
                x1, y1 = x0 + CELL_SIZE, y0 + CELL_SIZE
                
                if (row, col) == bot_position:
                    color = "red"
                elif (row, col) in self.knowledge_base:
                    color = "yellow"
                elif self.grid[row][col] == 0:
                    color = "black"
                else:
                    color = "white"
                
                canvas.create_rectangle(x0, y0, x1, y1, 
                                     fill=color, outline="gray")
        
        stats_text = (
            f"Possible positions: {len(self.knowledge_base)}\n"
            f"Movements: {self.actions_taken['movements']}\n"
            f"Sense actions: {self.actions_taken['sense_blocked']}"
        )
        canvas.create_text(10, 10, anchor="nw", text=stats_text, fill="blue")

def create_test_grid() -> List[List[int]]:
    """Create a test grid with guaranteed connected open spaces"""
    grid = [[0 for _ in range(D)] for _ in range(D)]
    
    # Block edges
    for i in range(D):
        grid[0][i] = grid[D-1][i] = grid[i][0] = grid[i][D-1] = 0
    
    # Create a more structured internal layout
    for i in range(1, D-1):
        for j in range(1, D-1):
            # Create some patterns to make positions more distinguishable
            if (i + j) % 3 == 0:
                grid[i][j] = 0
            else:
                grid[i][j] = 1
    
    # Ensure some paths exist
    for i in range(2, D-2, 2):
        for j in range(2, D-2, 2):
            grid[i][j] = 1
    
    return grid

def demo_baseline_bot():
    # Create grid
    grid = create_test_grid()
    
    # Find valid starting position
    open_cells = [(i, j) for i in range(1, D-1) for j in range(1, D-1) 
                  if grid[i][j] == 1]
    true_position = random.choice(open_cells)
    
    # Create and run bot
    bot = BaselineBot(grid)
    final_position = bot.locate_position(true_position, visualize=True)
    
    print("\nResults:")
    print(f"Initial position: {true_position}")
    print(f"Final position: {final_position}")
    print(f"Actions taken: {bot.actions_taken}")
    print(f"Position correctly identified: {final_position == true_position}")

if __name__ == '__main__':
    demo_baseline_bot()