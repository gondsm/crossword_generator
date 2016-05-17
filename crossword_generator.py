#!/usr/bin/python3
""" Crossword Generator

This script takes a list of words and creates a new latex table representing a
crosswod puzzle, which is then printed to PDF, and can be printed to actual,
if you're one of those people.
"""


def read_word_list(filename):
    """ This function reads the file and returns the words read. It expects a
    file where each word is in a line.
    """
    # Initialize words list
    words = []

    # Quick'n'dirty file reading
    with open(filename) as words_file:
        for line in words_file:
            words.append(line.strip())

    return words

def generate_grid(words, dim):
    """ This function receives a list of words and creates a new grid, which
    represents our puzzle. The newly-created grid is of dimensions
    dim[0] * dim[1] (rows * columns).
    TODO: detail algorithm
    """

def write_grid(grid, screen = False):
    """ This function receives the generated grid and writes it to the file (or
    to the screen, if that's what we want). The grid is expected to be a list
    of lists.
    """
    if screen is True:
        # Print grid to the screen
        print(grid)
    else:
        # Print grid to the file and compile
        ...

if __name__ == "__main__":
    words = read_word_list("words.txt")
    grid = generate_grid(words, [20,20])
    write_grid(grid)
