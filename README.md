# Conway's Game of Life
A cellular automata simulator written in Python with TkInter GUI library.
This is a feature-complete implementation allowing for designing your own boards on the fly.

## What works (and what doesn't - yet)
- [x] Base algorithm with GUI
- [x] Board drawing
- [x] Support for Life, Plaintext and RLE formats
- [x] Variable size, bounded/toroidal board (toggleable)
- [x] Single-generation trails
- [x] Speed control
- [x] Theme selection
- [x] Support for custom rulesets (next: changeable in GUI)
- [ ] Support for SOF and MCell formats
- [ ] Pattern rotation
- [ ] Infinite canvas (not planned)

## Goals
- All previously mentioned unimplemented things (except infinite canvas)
- Dynamic cell size (ensuring window size isn't bigger than the screen)
- Pattern transparency (not placing dead cells as an option)
- GUI refactor

The game autoloads patterns if they are in the same directory in a `patterns` folder. Once loaded, they're present in the pattern selection menu, placeable by clicking on the canvas (clicked cell is the top-left cell of the pattern's bounding box).

### Board design:
LMB - set cell state to alive
RMB - set cell state to dead
Supports dragging for faster designing.

This is an early stage prototype and the GUI is not in its final form. A few buttons are misplaced and their size is not yet properly defined. Functionality was a priority. You might encounter a few issues until it's resolved.

This code uses a simple, naive algorithm - running the program at full speed may consume plenty of resources and heat up your CPU.

Apart from the issues mentioned, it's functional. Have fun! 😇
