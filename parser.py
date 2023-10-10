import numpy as np
from pathlib import Path
from glob import glob

# Extensions
exts = ("txt", "cells", "rle", "l", "lif", "life" "sof", "mcl")

def convert_board(char):
    if char in ("O", "*"):
        return 1
    elif char != ".":
        print(f"WARNING: Invalid character: {char} (ignoring)")
    return 0

def parse_board(pattern):
        i = 0
        while i < len(pattern):
            if pattern[i][0] in ("#", "!"):
                pattern.pop(i)
            else:
                temp = pattern[i]
                pattern[i] = []
                for j in range(len(temp)):
                    pattern[i].append(convert_board(temp[j]))
                i += 1
        pattern = np.array(pattern)
        return pattern

def parse(directory):
    ext = directory.split(".")[-1].lower()
    # Check file extension
    if ext in exts:
        with open(directory, "r") as f:
            pattern = [line.strip() for line in f.readlines()]
    else:
        print(f"Unsupported file extension: {ext}")
        return
    # Parse Plaintext
    if ext in ("txt", "cells"):
        if "!Name" in pattern[0]:
            name = pattern[0].lstrip("!Name: ")
        else:
            name = directory.split("/")[-1].rsplit(".", 1)[0].replace("_", " ").capitalize()
        pattern = parse_board(pattern)
    # Parse Life
    elif ext in ("lif", "life"):
        name = directory.split("/")[-1].rsplit(".", 1)[0].replace("_", " ").capitalize()
        if "5" in pattern[0] or "2" in pattern[0]:
            pattern = parse_board(pattern)
        elif "6" in pattern[0]:
            coord_x = [int(line.split()[0]) for line in pattern if "#" not in line]
            coord_y = [int(line.split()[1]) for line in pattern if "#" not in line]
            size_x = max(coord_x) - min(coord_x) + 1
            size_y = max(coord_y) - min(coord_y) + 1
            offset_x = min(coord_x)
            offset_y = min(coord_y)
            coord_x = [x - offset_x for x in coord_x]
            coord_y = [y - offset_y for y in coord_y]
            pattern = np.zeros((size_y, size_x))
            for n in range(len(coord_x)):
                pattern[coord_y[n], coord_x[n]] = 1
        else:
            raise ValueError("The version of Life format defined in this pattern is not supported")
    # Parse RLE
    elif ext == "rle" or ext == "l":
        if "#N" in pattern[0]:
            name = pattern[0].lstrip("#N ")
        else:
            name = directory.split("/")[-1].rsplit(".", 1)[0].replace("_", " ").capitalize()
        pattern = [line for line in pattern if line[0] != "#"]
        rules = pattern[0].split(",")
        size_x = int(rules[0].strip("x= "))
        size_y = int(rules[1].strip("y= "))
        # TODO: Implement gamerule parsing
        temp = pattern[1:]
        string = ""
        pattern = np.zeros((size_y, size_x))
        for line in temp:
            string += line
        temp = ""
        i = 0
        x = 0
        y = 0
        try:
            while string[i] != "!":
                if string[i].isdigit():
                    temp += string[i]
                elif string[i] == "$":
                    y += 1
                    x = 0
                else:
                    if len(temp) == 0:
                        temp = 1
                    if string[i] != "b":
                        pattern[y, [n for n in range(x, x + int(temp))]] = 1
                    x += int(temp)
                    temp = ""
                i += 1
        except IndexError:
            print("Fallback - reached end of file (consider adding an exclamation mark to the pattern file's end)")
    # Parse SOF
    elif ext == "sof":
        pass # TODO: Implement SOF
    # Parse MCell
    elif ext == "mcl":
        pass # TODO: Implement MCell
    # Throw error on other file types
    else:
        raise ValueError("Invalid file extension")
    print(f"Loaded pattern: {name}")
    return name, pattern

def generate_pattern_list():
    directories = []
    templates = {}
    directory = str(Path(__file__).parent / "patterns/**/*.")
    for ext in exts:
        directories.extend(glob(directory + ext, recursive=True))
    for pattern in directories:
        name, pattern = parse(pattern)
        templates[name] = pattern
    print()
    return templates
