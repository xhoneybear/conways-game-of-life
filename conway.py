"""Conway's Game of Life GUI and logic."""

import numpy as np
import tkinter as tk

from parser import generate_pattern_list
from config import *


class Conway:
    def use_pattern(self, pattern):
        """
        Bind mouse click to pattern placement.

        args:
            pattern [str]: name of pattern
        """
        print("Select position...")
        self.canvas.bind("<Button-1>", lambda event: self.place_pattern(
            event.y // CELL, event.x // CELL, self.patterns[pattern]
        ))

    def place_pattern(self, y, x, array):
        """
        Place pattern on the board and unbind mouse click.

        args:
            y [int]: y position
            x [int]: x position
            array [np.array]: pattern array
        """
        self.canvas.bind("<Button-1>", lambda event: self.set_cell_state(1, event.y // CELL, event.x // CELL))
        for row in array:
            for c in row:
                self.set_cell_state(c, y, x)
                x += 1
            y += 1
            x -= array.shape[1]
        self.pattern.set("None")

    def set_cell_state(self, state, y, x):
        """
        Set cell state - alive or dead.

        args:
            state [int]: cell state
            y [int]: y position
            x [int]: x position
        """
        if 0 <= y <= HEIGHT-1 and 0 <= x <= WIDTH-1:
            if state == 1:
                self.board[y, x] = 1
                self.color_cell(x, y, "primary")
            else:
                self.board[y, x] = 0
                self.color_cell(x, y, "bg")

    def calculate_neighbors(self, y, x):
        """
        Calculate the number of live neighbors for a given cell.

        args:
            y [int]: y position
            x [int]: x position
        """
        if USE_QUEUE:
            if (x, y) in self.queue:
                return
            self.queue.add((x, y))

        if self.toroid.get():
            neighbors = sum(self.old_board[(y-h) % HEIGHT, (x-w) % WIDTH] \
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
                            neighbors += self.old_board[(y+h), (x+w)]
            else:
                neighbors = sum(self.old_board[y+h, x+w] \
                                for h in range(-1, 2) \
                                for w in range(-1, 2) \
                                if h != 0 or w != 0)
        # Apply the rules to the current cell
        if (self.old_board[y, x] == 0 and neighbors in REPRODUCE) \
        or (self.old_board[y, x] == 1 and neighbors in SURVIVE):
            self.board[y, x] = 1

    def proximal_calculation(self, y, x):
        """
        Calculate the number of live neighbors for cells around a live cell.

        args:
            y [int]: y position
            x [int]: x position
        """
        ranges = ((h, w) for h in range(-1, 2) for w in range(-1, 2))
        if self.toroid.get():
            for h, w in ranges:
                self.calculate_neighbors((y+h) % HEIGHT, (x+w) % WIDTH)
        else:
            for h, w in ranges:
                if 0 <= y+h < HEIGHT and 0 <= x+w < WIDTH:
                    self.calculate_neighbors(y+h, x+w)

    # Ruleset
    def evolve(self):
        """Calculate the next generation."""
        self.old_board = self.board
        self.board = np.zeros((HEIGHT, WIDTH))
        self.queue = set()
        # Count the number of live neighbors
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if OPTIMIZE:
                    if self.old_board[y, x] == 1:
                        self.proximal_calculation(y, x)
                else:
                    self.calculate_neighbors(y, x)

    def start(self):
        """Start the simulation."""
        self.PAUSED = False
        self.play_button.config(text="Pause", command=self.pause)
        self.play()

    def play(self):
        """Play the simulation."""
        if self.PAUSED is False:
            self.GEN += 1
            print(f"Generation {self.GEN}", end='\r')
            self.flush_cells()
            self.evolve()
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    if self.board[y, x] == 1:
                        if self.board[y, x] == self.old_board[y, x]:
                            self.color_cell(x, y, "primary")
                        else:
                            self.color_cell(x, y, "secondary")
                    elif self.trails.get() is True and self.old_board[y, x] == 1:
                        self.color_cell(x, y, "trail")
            delay = int(self.MAXSPEED/self.time.get())*10
            self.generation.config(text=f"Generation: {self.GEN}")
            self.canvas.update()
            self.canvas.after(delay, self.play)

    def pause(self):
        """Pause the simulation."""
        self.PAUSED = True
        self.play_button.config(text="Resume", command=self.start)

    def reset(self):
        """Reset the simulation."""
        self.PAUSED = True
        self.flush_cells()
        self.board = np.zeros((HEIGHT, WIDTH))
        self.cells = set()
        self.play_button.config(text="Start", command=self.start)
        self.GEN = 0

    def makeboard(self):
        """Create the game board."""
        self.canvas = tk.Canvas(self.root, width=CELL*WIDTH-1, height=CELL*HEIGHT-1)
        self.canvas.grid(row=0, column=0, columnspan=10)
        self.makelines()
        self.canvas.bind("<Button-1>", lambda event: self.set_cell_state(1, event.y // CELL, event.x // CELL))
        self.canvas.bind("<B1-Motion>", lambda event: self.set_cell_state(1, event.y // CELL, event.x // CELL))
        self.canvas.bind("<Button-3>", lambda event: self.set_cell_state(0, event.y // CELL, event.x // CELL))
        self.canvas.bind("<B3-Motion>", lambda event: self.set_cell_state(0, event.y // CELL, event.x // CELL))

    def makelines(self):
        """Draw the grid lines."""
        for y in range(HEIGHT):
            self.lines.add(self.canvas.create_line(0, y*CELL, CELL*WIDTH, y*CELL))
        for x in range(WIDTH):
            self.lines.add(self.canvas.create_line(x*CELL, 0, x*CELL, CELL*HEIGHT))

    def color_cell(self, x, y, color):
        """
        Color a cell.

        args:
            x [int]: x position
            y [int]: y position
            color [str]: cell color
        """
        self.cells.add((self.canvas.create_rectangle(
            x*CELL, y*CELL, (x+1)*CELL, (y+1)*CELL,
            fill=globals()[color], outline=grid), color
        ))

    def flush_cells(self):
        """Clear the cells from the board."""
        for cell in self.cells:
            self.canvas.delete(cell[0])
        self.cells = set()

    def refresh_grid(self):
        """Remake the grid on property change."""
        global HEIGHT, WIDTH, CELL
        HEIGHT = self.pre_height.get()
        WIDTH = self.pre_width.get()
        CELL = self.pre_cell.get()
        self.canvas.destroy()
        self.makeboard()
        self.change_theme(self.theme.get())
        self.reset()

    def randomize_board(self):
        """Randomize the game board."""
        self.reset()
        self.board = np.random.randint(2, size=(HEIGHT, WIDTH))
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if self.board[y, x] == 1:
                    self.color_cell(x, y, "primary")

    def change_theme(self, theme):
        """
        Change the theme.

        args:
            theme [str]: theme to set
        """
        global primary, secondary, trail, grid, bg
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

        self.update_style()

        self.root.config(bg=bg)
        self.canvas.config(bg=bg)
        self.pattern_menu.config(**style_button)
        self.randomize.config(**style_button)
        self.generation.config(**style_button)
        self.width_frame.config(**style_frame)
        self.width_control.config(**style_frame)
        self.height_frame.config(**style_frame)
        self.height_control.config(**style_frame)
        self.cell_frame.config(**style_frame)
        self.cell_control.config(**style_frame)
        self.speed_frame.config(**style_frame)
        self.speed_control.config(**style_slider)
        self.toroid_toggle.config(**style_button)
        self.trail_toggle.config(**style_button)
        self.theme_menu.config(**style_button)
        self.apply.config(**style_button)
        self.play_button.config(**style_button)
        self.reset_button.config(**style_button)

        for cell in self.cells:
            self.canvas.itemconfig(cell[0], fill=globals()[cell[1]])

        for line in self.lines:
            self.canvas.itemconfig(line, fill=grid)

    def update_style(self):
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
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Conway's Game of Life")

        # Engine variables
        self.board = np.zeros((HEIGHT, WIDTH))
        self.GEN = 0
        self.time = tk.DoubleVar()
        self.time.set(100)
        self.PAUSED = False
        self.cells = set()
        self.lines = set()

        # Patterns
        self.pattern = tk.StringVar()
        self.pattern.set("None")
        self.patterns = generate_pattern_list()
        # TODO: Implement pattern rotation

        # Board properties
        self.toroid = tk.BooleanVar()
        self.trails = tk.BooleanVar()

        ### Main window

        # Menu bar
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        # TODO: Populate menu with options

        # Board
        self.makeboard()

        # Pattern choice
        self.pattern_menu = tk.OptionMenu(self.root, self.pattern, *self.patterns, command=self.use_pattern)
        self.pattern_menu.config()
        self.pattern_menu.grid(row=1, column=0)

        # Randomize button
        self.randomize = tk.Button(self.root, text="Randomize", command=self.randomize_board)
        self.randomize.grid(row=1, column=1)

        # Generation label
        self.generation = tk.Label(self.root, text=f"Generation {self.GEN}")
        self.generation.grid(row=1, column=2)

        # Width
        self.width_frame = tk.LabelFrame(self.root, text="Width")
        self.width_frame.grid(row=1, column=3)
        self.pre_width = tk.IntVar()
        self.pre_width.set(WIDTH)
        self.width_control = tk.Spinbox(self.width_frame, from_=10, to=200, width=5, textvariable=self.pre_width)
        self.width_control.pack()

        # Height
        self.height_frame = tk.LabelFrame(self.root, text="Height")
        self.height_frame.grid(row=1, column=4)
        self.pre_height = tk.IntVar()
        self.pre_height.set(HEIGHT)
        self.height_control = tk.Spinbox(self.height_frame, from_=10, to=200, width=5, textvariable=self.pre_height)
        self.height_control.pack()

        # Cell size
        self.cell_frame = tk.LabelFrame(self.root, text="Cell size")
        self.cell_frame.grid(row=1, column=5)
        self.pre_cell = tk.IntVar()
        self.pre_cell.set(CELL)
        self.cell_control = tk.Spinbox(self.cell_frame, from_=1, to=100, width=5, textvariable=self.pre_cell)
        self.cell_control.pack()

        # Toroidal board
        self.toroid_toggle = tk.Checkbutton(self.root, text="Toroidal", variable=self.toroid)
        self.toroid_toggle.grid(row=2, column=2)

        # Trails
        self.trail_toggle = tk.Checkbutton(self.root, text="Trails", variable=self.trails)
        self.trail_toggle.grid(row=2, column=3)

        # Themes
        self.themes = ("Light", "Dark", "Orchid", "Explosive", "Aquatic", "Meadow")
        self.theme = tk.StringVar()
        self.theme.set(DEFAULT_THEME)
        self.theme_menu = tk.OptionMenu(self.root, self.theme, *self.themes, command=self.change_theme)
        self.theme_menu.config()
        self.theme_menu.grid(row=2, column=4)

        # Size apply button
        self.apply = tk.Button(self.root, text="Apply", command=self.refresh_grid)
        self.apply.grid(row=2, column=5)

        # Speed
        self.MAXSPEED = 100
        self.speed_frame = tk.LabelFrame(self.root, text="Speed")
        self.speed_frame.grid(row=2, column=6, columnspan=4, rowspan=2)
        self.sleep_var = tk.DoubleVar()
        self.speed_control = tk.Scale(
            self.speed_frame, from_=1, to=self.MAXSPEED,
            resolution=0.1, orient=tk.HORIZONTAL, variable=self.time
        )
        self.speed_control.pack()

        # Game control buttons
        self.play_button = tk.Button(self.root, text="Start", command=self.start)
        self.play_button.grid(row=3, column=0)
        self.reset_button = tk.Button(self.root, text="Reset", command=self.reset)
        self.reset_button.grid(row=3, column=1)

        # Apply theme
        self.change_theme(DEFAULT_THEME)

        tk.mainloop()

Conway()
