# Board size
height = 100
width = 100
cell = 10  # size in px

# Rules
survive = [2, 3]
reproduce = [3]
# TODO: Add gamerule toggles

# Themes
# Available: "Light", "Dark", "Orchid", "Explosive", "Aquatic", "Meadow"
default_theme = "Dark"

# Optimization

# Use proximal neighbor calculation
# Greatly improves speed on large boards
optimize = True
# Use queue to avoid recalculating neighbors
# Lowers CPU usage, increases RAM usage
use_queue = True
