"""Conway's Game of Life GUI and logic."""

import numpy as np
import tkinter as tk

from parser import generate_pattern_list
from config import *


def use_pattern(pattern):
    """
    Bind mouse click to pattern placement.

    args:
        pattern [str]: name of pattern
    """
    print("Select position...")
    canvas.bind("<Button-1>", lambda event: place_pattern(
        event.y // CELL, event.x // CELL, patterns[pattern]
    ))

def place_pattern(y, x, array):
    """
    Place pattern on the board and unbind mouse click.

    args:
        y [int]: y position
        x [int]: x position
        array [np.array]: pattern array
    """
    canvas.bind("<Button-1>", lambda event: set_cell_state(1, event.y // CELL, event.x // CELL))
    for row in array:
        for c in row:
            set_cell_state(c, y, x)
            x += 1
        y += 1
        x -= array.shape[1]
    pattern.set("None")

def set_cell_state(state, y, x):
    """
    Set cell state - alive or dead.

    args:
        state [int]: cell state
        y [int]: y position
        x [int]: x position
    """
    if 0 <= y <= HEIGHT-1 and 0 <= x <= WIDTH-1:
        if state == 1:
            board[y, x] = 1
            color_cell(x, y, "primary")
        else:
            board[y, x] = 0
            color_cell(x, y, "bg")

def calculate_neighbors(y, x):
    """
    Calculate the number of live neighbors for a given cell.

    args:
        y [int]: y position
        x [int]: x position
    """
    if USE_QUEUE:
        if (x, y) in queue:
            return
        queue.add((x, y))

    if toroid.get():
        neighbors = sum(old_board[(y-h) % HEIGHT, (x-w) % WIDTH] \
                        for h in range(-1, 2) \
                        for w in range(-1, 2) \
                        if h != 0 or w != 0)
    else:
        if y in (0, HEIGHT-1) or x in (0, WIDTH-1):
            neighbors = 0
            for h in range(-1, 2):
                for w in range(-1, 2):
                    if h == 0 and w == 0:
                        continue
                    if 0 <= y+h < HEIGHT and 0 <= x+w < WIDTH:
                        neighbors += old_board[(y+h), (x+w)]
        else:
            neighbors = sum(old_board[y+h, x+w] \
                            for h in range(-1, 2) \
                            for w in range(-1, 2) \
                            if h != 0 or w != 0)
    # Apply the rules to the current cell
    if (old_board[y, x] == 0 and neighbors in REPRODUCE) \
    or (old_board[y, x] == 1 and neighbors in SURVIVE):
        board[y, x] = 1

def proximal_calculation(y, x):
    """
    Calculate the number of live neighbors for cells around a live cell.

    args:
        y [int]: y position
        x [int]: x position
    """
    ranges = ((h, w) for h in range(-1, 2) for w in range(-1, 2))
    if toroid.get():
        for h, w in ranges:
            calculate_neighbors((y+h) % HEIGHT, (x+w) % WIDTH)
    else:
        for h, w in ranges:
            if 0 <= y+h < HEIGHT and 0 <= x+w < WIDTH:
                calculate_neighbors(y+h, x+w)

# Ruleset
def evolve():
    """Calculate the next generation."""
    global board, old_board, queue
    old_board = board
    board = np.zeros((HEIGHT, WIDTH))
    queue = set()
    # Count the number of live neighbors
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if OPTIMIZE:
                if old_board[y, x] == 1:
                    proximal_calculation(y, x)
            else:
                calculate_neighbors(y, x)

def start():
    """Start the simulation."""
    global PAUSED
    PAUSED = False
    play_button.config(text="Pause", command=pause)
    play()

def play():
    """Play the simulation."""
    global GEN
    if PAUSED is False:
        GEN += 1
        print(f"Generation {GEN}", end='\r')
        flush_cells()
        evolve()
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if board[y, x] == 1:
                    if board[y, x] == old_board[y, x]:
                        color_cell(x, y, "primary")
                    else:
                        color_cell(x, y, "secondary")
                elif trails.get() is True and old_board[y, x] == 1:
                    color_cell(x, y, "trail")
        delay = int(MAXSPEED/time.get())*10
        generation.config(text=f"Generation: {GEN}")
        canvas.update()
        canvas.after(delay, play)

def pause():
    """Pause the simulation."""
    global PAUSED
    PAUSED = True
    play_button.config(text="Resume", command=start)

def reset():
    """Reset the simulation."""
    global board, cells, PAUSED, GEN
    PAUSED = True
    flush_cells()
    board = np.zeros((HEIGHT, WIDTH))
    cells = set()
    play_button.config(text="Start", command=start)
    GEN = 0

def makeboard():
    """Create the game board."""
    global canvas
    canvas = tk.Canvas(root, width=CELL*WIDTH-1, height=CELL*HEIGHT-1)
    canvas.grid(row=0, column=0, columnspan=10)
    makelines()
    canvas.bind("<Button-1>", lambda event: set_cell_state(1, event.y // CELL, event.x // CELL))
    canvas.bind("<B1-Motion>", lambda event: set_cell_state(1, event.y // CELL, event.x // CELL))
    canvas.bind("<Button-3>", lambda event: set_cell_state(0, event.y // CELL, event.x // CELL))
    canvas.bind("<B3-Motion>", lambda event: set_cell_state(0, event.y // CELL, event.x // CELL))

def makelines():
    """Draw the grid lines."""
    for y in range(HEIGHT):
        lines.add(canvas.create_line(0, y*CELL, CELL*WIDTH, y*CELL))
    for x in range(WIDTH):
        lines.add(canvas.create_line(x*CELL, 0, x*CELL, CELL*HEIGHT))

def color_cell(x, y, color):
    """
    Color a cell.

    args:
        x [int]: x position
        y [int]: y position
        color [str]: cell color
    """
    cells.add((canvas.create_rectangle(
        x*CELL, y*CELL, (x+1)*CELL, (y+1)*CELL,
        fill=globals()[color], outline=grid), color
    ))

def flush_cells():
    """Clear the cells from the board."""
    global cells
    for cell in cells:
        canvas.delete(cell[0])
    cells = set()

def refresh_grid():
    """Remake the grid on property change."""
    global HEIGHT, WIDTH, CELL
    HEIGHT = pre_height.get()
    WIDTH = pre_width.get()
    CELL = pre_cell.get()
    canvas.destroy()
    makeboard()
    change_theme(theme.get())
    reset()

def randomize_board():
    """Randomize the game board."""
    global board
    reset()
    board = np.random.randint(2, size=(HEIGHT, WIDTH))
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if board[y, x] == 1:
                color_cell(x, y, "primary")

def change_theme(theme):
    """
    Change the theme.

    args:
        theme [str]: theme to set
    """
    global primary, secondary, trail, bg, grid
    if theme == "Light":
        primary = "black"
        secondary = "gray40"
        trail = "gray75"
        bg = "white"
    elif theme == "Dark":
        primary = "white"
        secondary = "gray60"
        trail = "gray25"
        bg = "black"
    elif theme == "Orchid":
        primary = "violet"
        secondary = "purple"
        trail = "purple4"
        bg = "black"
    elif theme == "Explosive":
        primary = "red"
        secondary = "darkorange"
        trail = "yellow"
        bg = "black"
    elif theme == "Aquatic":
        primary = "turquoise"
        secondary = "teal"
        trail = "seagreen"
        bg = "black"
    elif theme == "Meadow":
        primary = "gold"
        secondary = "pink"
        trail = "white"
        bg = "green"

    grid = "gray10"

    update_style()

    root.config(bg=bg)
    canvas.config(bg=bg)
    pattern_menu.config(**style_button)
    randomize.config(**style_button)
    generation.config(**style_button)
    width_frame.config(**style_frame)
    width_control.config(**style_frame)
    height_frame.config(**style_frame)
    height_control.config(**style_frame)
    cell_frame.config(**style_frame)
    cell_control.config(**style_frame)
    speed_frame.config(**style_frame)
    speed_control.config(**style_slider)
    toroid_toggle.config(**style_button)
    trail_toggle.config(**style_button)
    theme_menu.config(**style_button)
    apply.config(**style_button)
    play_button.config(**style_button)
    reset_button.config(**style_button)

    for cell in cells:
        canvas.itemconfig(cell[0], fill=globals()[cell[1]])

    for line in lines:
        canvas.itemconfig(line, fill=grid)

def update_style():
    """Update style variables."""
    global style_frame, style_button, style_slider
    style = {
        'bg': bg,
        'fg': primary,
        'bd': 0,
        'relief': tk.FLAT,
        'highlightthickness': 0,
    }

    style_frame = {
        'bd': 10,
    }
    style_frame.update(style)

    style_button = {
        'activebackground': trail,
        'activeforeground': primary,
        'padx': 10,
        'pady': 10
    }
    style_button.update(style)

    style_slider = {
        'troughcolor': primary,
    }
    style_slider.update(style)

### GUI ###

## Init
root = tk.Tk()
root.title("Conway's Game of Life")

# Engine variables
board = np.zeros((HEIGHT, WIDTH))
GEN = 0
time = tk.DoubleVar()
time.set(100)
PAUSED = False
cells = set()
lines = set()

# Patterns
pattern = tk.StringVar()
pattern.set("None")
patterns = generate_pattern_list()
# TODO: Implement pattern rotation

# Board properties
toroid = tk.BooleanVar()
trails = tk.BooleanVar()

### Main window

# Menu bar
menubar = tk.Menu(root)
root.config(menu=menubar)
# TODO: Populate menu with options

# Board
makeboard()

# Pattern choice
pattern_menu = tk.OptionMenu(root, pattern, *patterns, command=use_pattern)
pattern_menu.config()
pattern_menu.grid(row=1, column=0)

# Randomize button
randomize = tk.Button(root, text="Randomize", command=randomize_board)
randomize.grid(row=1, column=1)

# Generation label
generation = tk.Label(root, text=f"Generation {GEN}")
generation.grid(row=1, column=2)

# Width
width_frame = tk.LabelFrame(root, text="Width")
width_frame.grid(row=1, column=3)
pre_width = tk.IntVar()
pre_width.set(WIDTH)
width_control = tk.Spinbox(width_frame, from_=10, to=200, width=5, textvariable=pre_width)
width_control.pack()

# Height
height_frame = tk.LabelFrame(root, text="Height")
height_frame.grid(row=1, column=4)
pre_height = tk.IntVar()
pre_height.set(HEIGHT)
height_control = tk.Spinbox(height_frame, from_=10, to=200, width=5, textvariable=pre_height)
height_control.pack()

# Cell size
cell_frame = tk.LabelFrame(root, text="Cell size")
cell_frame.grid(row=1, column=5)
pre_cell = tk.IntVar()
pre_cell.set(CELL)
cell_control = tk.Spinbox(cell_frame, from_=1, to=100, width=5, textvariable=pre_cell)
cell_control.pack()

# Toroidal board
toroid_toggle = tk.Checkbutton(root, text="Toroidal", variable=toroid)
toroid_toggle.grid(row=2, column=2)

# Trails
trail_toggle = tk.Checkbutton(root, text="Trails", variable=trails)
trail_toggle.grid(row=2, column=3)

# Themes
themes = ("Light", "Dark", "Orchid", "Explosive", "Aquatic", "Meadow")
theme = tk.StringVar()
if not DEFAULT_THEME or DEFAULT_THEME not in themes:
    DEFAULT_THEME = "Dark"
theme.set(DEFAULT_THEME)
theme_menu = tk.OptionMenu(root, theme, *themes, command=change_theme)
theme_menu.config()
theme_menu.grid(row=2, column=4)

# Size apply button
apply = tk.Button(root, text="Apply", command=refresh_grid)
apply.grid(row=2, column=5)

# Speed
MAXSPEED = 100
speed_frame = tk.LabelFrame(root, text="Speed")
speed_frame.grid(row=2, column=6, columnspan=4, rowspan=2)
sleep_var = tk.DoubleVar()
speed_control = tk.Scale(
    speed_frame, from_=1, to=MAXSPEED,
    resolution=0.1, orient=tk.HORIZONTAL, variable=time
)
speed_control.pack()

# Game control buttons
play_button = tk.Button(root, text="Start", command=start)
play_button.grid(row=3, column=0)
reset_button = tk.Button(root, text="Reset", command=reset)
reset_button.grid(row=3, column=1)

# Apply theme
change_theme(DEFAULT_THEME)

tk.mainloop()
