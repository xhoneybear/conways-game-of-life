import numpy as np
import tkinter as tk
from parser import generate_pattern_list
from config import *

def use_pattern(pattern):
    print("Select position...")
    canvas.bind("<Button-1>", lambda event: place_pattern(event.y // cell, event.x // cell, patterns[pattern]))

def place_pattern(y, x, array):
    canvas.bind("<Button-1>", lambda event: set_cell_state(1, event.y // cell, event.x // cell))
    for row in array:
        for c in row:
            set_cell_state(c, y, x)
            x += 1
        y += 1
        x -= array.shape[1]
    pattern.set("None")

def set_cell_state(state, y, x):
    global board
    if 0 <= y <= height-1 and 0 <= x <= width-1:
        if state == 1:
            board[y, x] = 1
            color_cell(x, y, "primary")
        else:
            board[y, x] = 0
            color_cell(x, y, "bg")

def calculate_neighbors(y, x):
    if toroid.get() == True:
        neighbors = old_board[(y-1) % height, (x-1) % width] + \
                    old_board[(y-1) % height, x] + \
                    old_board[(y-1) % height, (x+1) % width] + \
                    old_board[y, (x-1) % width] + \
                    old_board[y, (x+1) % width] + \
                    old_board[(y+1) % height, (x-1) % width] + \
                    old_board[(y+1) % height, x] + \
                    old_board[(y+1) % height, (x+1) % width]
    else:
        if y in (0, height-1) or x in (0, width-1):
            neighbors = 0
            for h in range(-1, 2):
                for w in range(-1, 2):
                    if h == 0 and w == 0:
                        continue
                    if 0 <= y+h < height and 0 <= x+w < width:
                        neighbors += old_board[(y+h), (x+w)]
        else:
            neighbors = old_board[y-1, x-1] + \
                        old_board[y-1, x] + \
                        old_board[y-1, x+1] + \
                        old_board[y, x-1] + \
                        old_board[y, x+1] + \
                        old_board[y+1, x-1] + \
                        old_board[y+1, x] + \
                        old_board[y+1, x+1]
    return neighbors

def randomize_board():
    global board
    reset()
    board = np.random.randint(2, size=(height, width))
    for y in range(height):
        for x in range(width):
            if board[y, x] == 1:
                color_cell(x, y, "primary")

# Ruleset
def evolve():
    global board, old_board
    old_board = board
    board = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            # Count the number of live neighbors
            neighbors = calculate_neighbors(y, x)
            # Apply the rules to the current cell
            if old_board[y, x] == 0 and neighbors in reproduce:
                board[y, x] = 1
            elif old_board[y, x] == 1 and neighbors in survive:
                board[y, x] = 1

def start():
    global paused
    paused = False
    play_button.config(text="Pause", command=pause)
    play()

def play():
    global gen
    if paused == False:
        gen += 1
        print(f"Generation {gen}") # TODO: Move to GUI
        flush_cells()
        evolve()
        for y in range(height):
            for x in range(width):
                if board[y, x] == 1:
                    if board[y, x] == old_board[y, x]:
                        color_cell(x, y, "primary")
                    else:
                        color_cell(x, y, "secondary")
                elif trails.get() == True and old_board[y, x] == 1:
                    color_cell(x, y, "trail")
        canvas.update()
        canvas.after(int(time.get()*1000), play)

def pause():
    global paused
    paused = True
    play_button.config(text="Resume", command=start)

def reset():
    global board, cells, paused, gen
    paused = True
    flush_cells()
    board = np.zeros((height, width))
    cells = set()
    play_button.config(text="Start", command=start)
    gen = 0

def makeboard():
    global canvas
    canvas = tk.Canvas(root, width=cell*width-1, height=cell*height-1, bg=bg)
    canvas.grid(row=0, column=0, columnspan=10)
    makelines()
    canvas.bind("<Button-1>", lambda event: set_cell_state(1, event.y // cell, event.x // cell))
    canvas.bind("<B1-Motion>", lambda event: set_cell_state(1, event.y // cell, event.x // cell))
    canvas.bind("<Button-3>", lambda event: set_cell_state(0, event.y // cell, event.x // cell))
    canvas.bind("<B3-Motion>", lambda event: set_cell_state(0, event.y // cell, event.x // cell))

def makelines():
    for y in range(height):
        lines.add(canvas.create_line(0, y*cell, cell*width, y*cell, fill=grid))
    for x in range(width):
        lines.add(canvas.create_line(x*cell, 0, x*cell, cell*height, fill=grid))

def color_cell(x, y, color):
    cells.add((canvas.create_rectangle(x*cell, y*cell, (x+1)*cell, (y+1)*cell, fill=globals()[color], outline=grid), color))

def flush_cells():
    global cells
    for cell in cells:
        canvas.delete(cell[0])
    cells = set()

def refresh_grid():
    global height, width, cell
    height = pre_height.get()
    width = pre_width.get()
    cell = pre_cell.get()
    canvas.destroy()
    makeboard()
    reset()

def change_theme(theme):
    global primary, secondary, trail, bg, lines
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

    update_style()

    root.config(bg=bg)
    canvas.config(bg=bg)
    pattern_menu.config(**style_button)
    randomize.config(**style_button)
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

def update_style():
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
board = np.zeros((height, width))
gen = 0
time = tk.DoubleVar()
time.set(0)
paused = False
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

# Themes
theme = tk.StringVar()
theme.set("Light")
themes = ("Light", "Dark", "Orchid", "Explosive", "Aquatic", "Meadow")
primary = "black"
secondary = "gray40"
trail = "gray75"
bg = "white"
grid = "gray10"

update_style()

### Main window

# Menu bar
menubar = tk.Menu(root)
root.config(menu=menubar, bg=bg)
# TODO: Populate menu with options

# Board
makeboard()

# Pattern choice
pattern_menu = tk.OptionMenu(root, pattern, *patterns, command=use_pattern)
pattern_menu.config(**style_button)
pattern_menu.grid(row=1, column=0)

# Randomize button
randomize = tk.Button(root, text="Randomize", command=randomize_board, **style_button)
randomize.grid(row=1, column=1)

# Width
width_frame = tk.LabelFrame(root, text="Width", **style_frame)
width_frame.grid(row=1, column=3)
pre_width = tk.IntVar()
pre_width.set(width)
width_control = tk.Spinbox(width_frame, from_=10, to=200, width=5, textvariable=pre_width, **style_frame)
width_control.pack()

# Height
height_frame = tk.LabelFrame(root, text="Height", **style_frame)
height_frame.grid(row=1, column=4)
pre_height = tk.IntVar()
pre_height.set(height)
height_control = tk.Spinbox(height_frame, from_=10, to=200, width=5, textvariable=pre_height, **style_frame)
height_control.pack()

# Cell size
cell_frame = tk.LabelFrame(root, text="Cell size", **style_frame)
cell_frame.grid(row=1, column=5)
pre_cell = tk.IntVar()
pre_cell.set(cell)
cell_control = tk.Spinbox(cell_frame, from_=1, to=100, width=5, textvariable=pre_cell, **style_frame)
cell_control.pack()

# Toroidal board
toroid_toggle = tk.Checkbutton(root, text="Toroidal", variable=toroid, **style_button)
toroid_toggle.grid(row=2, column=2)

# Trails
trail_toggle = tk.Checkbutton(root, text="Trails", variable=trails, **style_button)
trail_toggle.grid(row=2, column=3)

# Theme
theme_menu = tk.OptionMenu(root, theme, *themes, command=change_theme)
theme_menu.config(**style_button)
theme_menu.grid(row=2, column=4)

apply = tk.Button(root, text="Apply", command=refresh_grid, **style_button)
apply.grid(row=2, column=5)

# Speed
speed_frame = tk.LabelFrame(root, text="Speed", **style_frame)
speed_frame.grid(row=2, column=6, columnspan=4, rowspan=2)
sleep_var = tk.DoubleVar()
speed_control = tk.Scale(speed_frame, from_=0, to=5, resolution=0.1, orient=tk.HORIZONTAL, variable=time, **style_slider)
speed_control.pack()

# Game control buttons
play_button = tk.Button(root, text="Start", command=start, **style_button)
play_button.grid(row=3, column=0)
reset_button = tk.Button(root, text="Reset", command=reset, **style_button)
reset_button.grid(row=3, column=1)

tk.mainloop()
