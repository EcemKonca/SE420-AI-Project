import tkinter as tk
from tkinter import ttk
from queue import PriorityQueue


class Node:
    def __init__(self, state, parent=None, action=None, cost=0, heuristic=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.heuristic = heuristic

    def __lt__(self, other):
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)


def is_valid_move(current, move, walls):  # Check if a move is valid (not wall) for the current state
    next_state = apply_move(current, move)
    return (
                   move == 'up' and current - 3 >= 0 and (current, current - 3) not in walls
                   or move == 'down' and current + 3 < 9 and (current, current + 3) not in walls
                   or move == 'left' and current % 3 != 0 and (current, current - 1) not in walls
                   or move == 'right' and current % 3 != 2 and (current, current + 1) not in walls
           ) and next_state not in walls


def apply_move(current, move):  # Apply a move to the current state and return the new state
    if move == 'up':
        return current - 3
    elif move == 'down':
        return current + 3
    elif move == 'left':
        return current - 1
    elif move == 'right':
        return current + 1
    return current


def parse_wall_input(walls_input):  # Parse wall input and convert it into a set of wall positions
    walls = set()
    for wall in walls_input.split(','):
        room1, room2 = wall.strip().upper()
        walls.add((ord(room1) - ord('A'), ord(room2) - ord('A')))
        walls.add((ord(room2) - ord('A'), ord(room1) - ord('A')))
    return walls


def print_path(node):  # Generate and return the path and cost from the start to the given node
    path = []
    cost = node.heuristic  # for a* first step
    while node:
        path.append(chr(ord('A') + node.state))
        if node.parent:
            cost += node.cost
        node = node.parent
    path.reverse()
    return path, cost


def uniform_cost_search(canvas, source, goal, walls):
    frontier = PriorityQueue()
    visited = set()

    start_node = Node(source)
    frontier.put((0, start_node))  # Use a tuple with cost as the first element

    expanded_nodes = 0
    result_path = None

    explored_nodes = []

    while not frontier.empty() and expanded_nodes < 10:
        current_cost, current_node = frontier.get()
        current_state = current_node.state

        if current_state == goal:
            expanded_nodes += 1
            explored_nodes.append(current_node)
            result_path = print_path(current_node)
            draw_grid(canvas, current_state, goal, walls, explored_nodes)
            canvas.update()
            canvas.after(500)  # Adjust the delay
            break

        if current_node.parent and current_node.parent.parent:
            grandparent_state = current_node.parent.parent.state
        else:
            grandparent_state = None

        if current_state != grandparent_state:
            visited.add(current_state)
            expanded_nodes += 1

            explored_nodes.append(current_node)  # Store explored nodes

            for move in ['up', 'down', 'left', 'right']:
                if is_valid_move(current_state, move, walls):
                    new_state = apply_move(current_state, move)
                    new_cost = (2 if move in ['right', 'left'] else 1)
                    new_node = Node(new_state, current_node, move, new_cost)
                    frontier.put((current_cost + new_cost, new_node))  # Include cumulative cost in the priority

                    # Draw grid with expanded nodes
                    draw_grid(canvas, current_state, goal, walls, explored_nodes)
                    canvas.update()
                    canvas.after(500)  # Adjust the delay

    return result_path, explored_nodes


def manhattan_distance(state, goal):
    state_row, state_col = divmod(state, 3)
    goal_row, goal_col = divmod(goal, 3)
    distance = abs(state_row - goal_row) + abs(state_col - goal_col)
    return distance


def astar_search(canvas, source, goal, walls):
    frontier = PriorityQueue()
    visited = set()

    start_node = Node(source, heuristic=manhattan_distance(source, goal))
    frontier.put((start_node.heuristic, start_node))  # Include the heuristic in the priority

    expanded_nodes = 0
    result_path = None

    explored_nodes = []

    while not frontier.empty() and expanded_nodes < 10:
        current_priority, current_node = frontier.get()
        current_state = current_node.state

        if current_state == goal:
            expanded_nodes += 1
            explored_nodes.append(current_node)
            result_path = print_path(current_node)
            draw_grid(canvas, current_state, goal, walls, explored_nodes)
            canvas.update()
            canvas.after(500)  # Adjust the delay
            break

        if current_node.parent and current_node.parent.parent:
            grandparent_state = current_node.parent.parent.state
        else:
            grandparent_state = None

        if current_state != grandparent_state:
            visited.add(current_state)
            expanded_nodes += 1

            explored_nodes.append(current_node)  # Store explored nodes

            for move in ['up', 'down', 'left', 'right']:
                if is_valid_move(current_state, move, walls):
                    new_state = apply_move(current_state, move)
                    new_heuristic = manhattan_distance(new_state, goal)
                    new_cost = (2 if move in ['right', 'left'] else 1)
                    total_cost = new_cost + current_node.heuristic
                    new_node = Node(new_state, current_node, move, new_cost, new_heuristic)
                    frontier.put((current_node.cost + total_cost,
                                  new_node))  # Include cumulative cost and heuristic in the priority

                    # Draw grid with expanded nodes
                    draw_grid(canvas, current_state, goal, walls, explored_nodes)
                    canvas.update()
                    canvas.after(500)  # Adjust the delay

    return result_path, explored_nodes


def draw_grid(canvas, robot_position, goal_position, walls, expanded_nodes):
    canvas.delete("all")

    # Define grid parameters
    cell_size = 50
    margin = 10

    for i in range(9):  # Rooms created here
        row, col = divmod(i, 3)
        x1 = col * cell_size + margin
        y1 = row * cell_size + margin
        x2 = x1 + cell_size
        y2 = y1 + cell_size

        room = chr(ord('A') + i)

        if i in walls:
            canvas.create_rectangle(x1, y1, x2, y2, fill="gray", outline="black")
            canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=room, fill="white")
        elif i == robot_position:
            canvas.create_rectangle(x1, y1, x2, y2, fill="blue", outline="black")
            canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=room, fill="white")
        elif i == goal_position:
            canvas.create_rectangle(x1, y1, x2, y2, fill="green", outline="black")
            canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=room, fill="white")
        else:
            canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")
            canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=room)

    # Highlight walls
    for wall in walls:
        room1, room2 = wall
        row1, col1 = divmod(room1, 3)
        row2, col2 = divmod(room2, 3)

        x1 = col1 * cell_size + margin
        y1 = row1 * cell_size + margin
        x2 = x1 + cell_size
        y2 = y1 + cell_size

        # Draw vertical wall to the right
        if col1 < 2 and (room1, room1 + 1) in walls:
            canvas.create_line(x2, y1, x2, y2, fill="purple", width=5)

        # Draw horizontal wall below
        if row1 < 2 and (room1, room1 + 3) in walls:
            canvas.create_line(x1, y2, x2, y2, fill="purple", width=5)


def print_grid(robot_position, goal_position, walls):
    for i in range(9):
        room = chr(ord('A') + i)
        if i in walls:
            print("##", end=' ')
        elif i == robot_position:
            print("R ", end=' ')
        elif i == goal_position:
            print("G ", end=' ')
        else:
            print(room, end=' ')
        if (i + 1) % 3 == 0:
            print()


def on_submit():
    try:
        source_input = source_entry.get().upper()
        goal_input = goal_entry.get().upper()
        walls_input = walls_entry.get()

        if not source_input or not goal_input or not walls_input:
            raise ValueError("Source, goal, and wall inputs cannot be empty.")

        source = ord(source_input) - ord('A')
        goal = ord(goal_input) - ord('A')

        walls = parse_wall_input(walls_input)

        selected_strategy = strategy_var.get()

        if selected_strategy == 1:
            result_path, explored_nodes = uniform_cost_search(grid_canvas, source, goal, walls)
            strategy_name = "Uniform Cost Search"
        elif selected_strategy == 2:
            result_path, explored_nodes = astar_search(grid_canvas, source, goal, walls)
            strategy_name = "A* Search with Manhattan Distance Heuristic"
        else:
            result_path = None
            cost = 0
            strategy_name = "Unknown Strategy"

        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"{strategy_name} Result:\n")

        # Display each step
        for i, node in enumerate(explored_nodes):
            result_text.insert(tk.END, f"\nStep {i + 1} - Expanded Node: {chr(ord('A') + node.state)}:\n")
            path, cost = print_path(node)
            result_text.insert(tk.END, f"Path: {' -> '.join(map(str, path))}\n")
            result_text.insert(tk.END, f"Total Cost: {cost}\n")
            # Print path, cost, and grid in the terminal
            print(f"\nStep {i + 1} - Expanded Node: {chr(ord('A') + node.state)}:")
            print_grid(node.state, goal, walls)
            print(f"Path: {' -> '.join(map(str, path))}")
            print(f"Total Cost: {cost}")

        expanded_nodes_str = ', '.join(chr(ord('A') + node.state) for node in explored_nodes)
        result_text.insert(tk.END, f"Expansion Order: {expanded_nodes_str}\n")

        if len(explored_nodes) >= 10:
            result_text.insert(tk.END, "Goal not reached within 10 expanded nodes.\n")
        result_text.config(state=tk.DISABLED)

    except ValueError as e:
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Error: {str(e)}\n")
        result_text.config(state=tk.DISABLED)


# GUI Setup
root = tk.Tk()
root.title("Robot Game Solver")

frame = ttk.Frame(root, padding="10")
frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

source_label = ttk.Label(frame, text="Source position (A-G):")
source_entry = ttk.Entry(frame, width=5)

goal_label = ttk.Label(frame, text="Goal position (A-G):")
goal_entry = ttk.Entry(frame, width=5)

walls_label = ttk.Label(frame, text="Walls (comma-separated, e.g., AB,CD):")
walls_entry = ttk.Entry(frame, width=20)

strategy_var = tk.IntVar()
strategy_label = ttk.Label(frame, text="Select Search Strategy:")
uniform_cost_radio = ttk.Radiobutton(frame, text="Uniform Cost Search", variable=strategy_var, value=1)
astar_radio = ttk.Radiobutton(frame, text="A* Search with Manhattan Distance Heuristic", variable=strategy_var, value=2)

submit_button = ttk.Button(frame, text="Submit", command=on_submit)

result_text = tk.Text(frame, height=10, width=55, state=tk.DISABLED)

# Canvas widget for displaying the grid
grid_canvas = tk.Canvas(frame, width=150, height=150)
grid_canvas.grid(column=0, row=8, columnspan=2, pady=10)

# Grid layout
source_label.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)
source_entry.grid(column=1, row=0, padx=5, pady=5)

goal_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)
goal_entry.grid(column=1, row=1, padx=5, pady=5)

walls_label.grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)
walls_entry.grid(column=1, row=2, padx=5, pady=5)

strategy_label.grid(column=0, row=3, columnspan=2, sticky=tk.W, padx=5, pady=5)
uniform_cost_radio.grid(column=0, row=4, columnspan=2, sticky=tk.W, padx=5, pady=5)
astar_radio.grid(column=0, row=5, columnspan=2, sticky=tk.W, padx=5, pady=5)

submit_button.grid(column=0, row=6, columnspan=2, pady=10)

result_text.grid(column=0, row=7, columnspan=2, pady=10)

# Run the GUI
root.mainloop()
