"""Configuration file."""

# Board size
HEIGHT = 150
WIDTH = 150
CELL = 5  # size in px

# Rules
SURVIVE = [2, 3]
REPRODUCE = [3]
# TODO: Add gamerule toggles

# Themes
# Available: "Light", "Dark", "Orchid", "Explosive", "Aquatic", "Meadow"
DEFAULT_THEME = "Dark"

# Optimization

# Use proximal neighbor calculation
# Greatly improves speed on large boards
OPTIMIZE = True
# Use queue to avoid recalculating neighbors
# Lowers CPU usage, increases RAM usage
USE_QUEUE = True
