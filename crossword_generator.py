#!/usr/bin/python3
""" Crossword Generator

This script takes a list of words and creates a new latex table representing a
crosswod puzzle, which is then printed to PDF, and can be printed to actual,
if you're one of those people.
"""

# STL imports
import random


# Auxiliary Functions
def generate_possibilities(words):
    """ This function generates the possibilities (see generate_grid) """
    # Initialize the list of possibilities
    possibilities = []

    # For every word in the list
    #for word in words:


def is_valid(possibility, grid):
    """ This function determines whether a possibility is still valid in the
    given grid.
    TODO: Explain rules
    """
    ...


# Basic Functions
def read_word_list(filename, n_words=100):
    """ This function reads the file and returns the words read. It expects a
    file where each word is in a line.
    """
    # Initialize words lists
    words = []
    selected_words = []

    # Quick'n'dirty file reading
    with open(filename) as words_file:
        for line in words_file:
            words.append(line.strip())

    # Select n_words words
    while len(selected_words) < n_words:
        # Choose candidate randomly
        candidate = words[random.randint(0, len(words)-1)]
        # Append candidate if it's not already there
        if candidate not in selected_words:
            selected_words.append(candidate)

    # ... and return the list
    return selected_words


def generate_grid(words, dim):
    """ This function receives a list of words and creates a new grid, which
    represents our puzzle. The newly-created grid is of dimensions
    dim[0] * dim[1] (rows * columns).

    Algorithm:
    This function operates by taking the words it receives and generating an
    expanded dictionary with all possible locations and directions of each
    word. It then adds words at random and, for each word added, removes all
    possibilities that are now invalid. This is done until the grid is complete
    or there are no more possibilities.

    Each possibility is a dictionary of the kind:
    p["word"] = the actual string
    p["location"] = the [i,j] list with the location
    p["D"] = the direction of the possibility (E for ->, S for down)
    """
    ...


def write_grid(grid, screen=False, out_file="table.tex"):
    """ This function receives the generated grid and writes it to the file (or
    to the screen, if that's what we want). The grid is expected to be a list
    of lists.
    """
    if screen is True:
        # Print grid to the screen
        for line in grid:
            print(line)
    else:
        # Print grid to the file and compile
        with open(out_file, "w") as texfile:
            # Write preamble
            texfile.write("\documentclass{article}" + "\n")
            texfile.write(r"\usepackage[utf8]{inputenc}" + "\n")
            texfile.write("\n")
            texfile.write(r"\begin{document}" + "\n")

            # Write table environment and format
            texfile.write(r"\begin{tabular}{|")
            for i in range(len(grid[0])):
                texfile.write(r"c|")
            texfile.write("}\n")

            # Write actual table
            for line in grid:
                for index, element in enumerate(line):
                    # This feels a bit hacky, suggestions appreciated
                    if index == len(line)-1:
                        texfile.write(element)
                    else:
                        texfile.write(element + " & ")

                texfile.write(r"\\" + "\n")

            # End environments
            texfile.write("\end{tabular}\n")
            texfile.write("\end{document}\n")

            # Compile
            # TODO


# Test cases
def test_write_grid():
    # Sample grid
    grid = [["a", "b", "c", "p"],
            ["e", "k", "l", "ç"],
            ["s", "g", "e", "ã"],
            ["s", "g", "e", "ã"],
            ["s", "g", "e", "ã"],
            ]

    # Write to screen and file
    write_grid(grid)
    write_grid(grid, True)

if __name__ == "__main__":
    words = read_word_list("words.txt")
    print(words)
    #grid = generate_grid(words, [20,20])
    #write_grid(grid)
    #test_write_grid()
