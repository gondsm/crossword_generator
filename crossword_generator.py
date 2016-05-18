#!/usr/bin/python3
""" Crossword Generator

This script takes a list of words and creates a new latex table representing a
crosswod puzzle, which is then printed to PDF, and can be printed to actual
paper, if you're one of those people.

TODO: Usage instructions
"""

# STL imports
import random
import pprint
import subprocess
import tempfile
import os
import shutil


# Auxiliary Functions
def generate_possibilities(words, dim):
    """ This function generates the possibilities (see generate_grid) """
    # Initialize the list of possibilities
    possibilities = []

    # For every word in the list
    for word in words:
        # D = E
        for i in range(dim[0]):
            for j in range(dim[1] - len(word)):
                possibilities.append({"word": word,
                                      "location": [i, j],
                                      "D": "E"})

        # D = S
        for i in range(dim[0] - len(word)):
            for j in range(dim[1]):
                possibilities.append({"word": word,
                                      "location": [i, j],
                                      "D": "S"})

    # ... and return all of the possibilities.
    return possibilities


def is_valid(possibility, grid):
    """ This function determines whether a possibility is still valid in the
    given grid. (see generate_grid)

    A possibility is deemed invalid if:
     -> it collides with any word that already exists, i.e. if any of its
     elements does not match the words already in the grid;
     -> it would be placed too close to another word, so that it would give rise
     to many short non-words;
     -> if the cell that precedes and succedes it in its direction is not empty.
    """
    # Import possibility to local vars, for clarity
    i = possibility["location"][0]
    j = possibility["location"][1]
    word = possibility["word"]
    D = possibility["D"]

    # Detect collisions and proximity
    for k, letter in enumerate(list(word)):
        if D is "E":
            # Collisions
            if grid[i][j+k] != 0 and grid[i][j+k] != letter:
                return False
            # Proximity
            if grid[i][j+k] == 0:
                if (i < len(grid)-1 and grid[i+1][j+k] != 0) or (i > 0 and grid[i-1][j+k] != 0):
                    return False
        if D is "S":
            # Collisions
            if grid[i+k][j] != 0 and grid[i+k][j] != letter:
                return False
            # Proximity
            if grid[i+k][j] == 0:
                if (j < len(grid[0])-1 and grid[i+k][j+1] != 0) or (j > 0 and grid[i+k][j-1] != 0):
                    return False

    # Start and End
    if D is "E":
        # If the preceding space isn't empty
        if j > 0 and grid[i][j-1] != 0:
            return False
        # If the succeding space isn't empy
        if j+len(word) < len(grid[0])-1 and grid[i][j+len(word)] != 0:
            return False
    if D is "S":
        # If the preceding space isn't empty
        if i > 0 and grid[i-1][j] != 0:
            return False
        # If the succeding space isn't empy
        if i+len(word) < len(grid)-1 and grid[i+len(word)][j] != 0:
            return False

    # If we can't find any collisions, it must be okay!
    return True


def is_disconnected(possibility, grid):
    """ This function determines whether a given possibility would be placed as
    a disconnected word on the grid, i.e. in a way that it crosses no other
    word.
    """
    # Import possibility to local vars, for clarity
    i = possibility["location"][0]
    j = possibility["location"][1]
    word = possibility["word"]
    D = possibility["D"]

    # Detect collisions and proximity
    for k, letter in enumerate(list(word)):
        if D is "E":
            # Collisions
            if grid[i][j+k] != 0:
                return False

        if D is "S":
            # Collisions
            if grid[i+k][j] != 0:
                return False

    # If nothing is detected, it must be disconnected!
    return True
    #return False

def add_word_to_grid(possibility, grid):
    """ Adds a possibility to the given grid, which is modified in-place.
    (see generate_grid)
    """
    # Import possibility to local vars, for clarity
    i = possibility["location"][0]
    j = possibility["location"][1]
    word = possibility["word"]

    # Word is left-to-right
    if possibility["D"] == "E":
        grid[i][j:len(list(word))+j] = list(word)
    # Word is top-to-bottom
    # (I can't seem to be able to use the slicing as above)
    if possibility["D"] == "S":
        for index, a in enumerate(list(word)):
            grid[i+index][j] = a


def draw_words(words, n_words=100):
    """ This function draws a number of words from the given (expectedly large)
    pool of words.
    """
    # Initialize list
    selected_words = []

    # If we have few words, we use them all
    if len(words) <= n_words:
        selected_words = words
    # If we have enough words, we have to select
    else:
        while len(selected_words) < n_words:
            # Choose candidate randomly
            candidate = words[random.randint(0, len(words)-1)]
            # Append candidate if its length is acceptable
            if len(candidate) > 1:
                selected_words.append(candidate)

    # ... and return the list
    return selected_words


# Basic Functions
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

    # and we're done
    return words


def generate_grid(words, dim):
    """ This function receives a list of words and creates a new grid, which
    represents our puzzle. The newly-created grid is of dimensions
    dim[0] * dim[1] (rows * columns).

    Algorithm:
    This function operates by taking the words it receives and generating an
    expanded dictionary with all possible locations and directions of each
    word. These are then filtered for words that are connected to words already
    in the grid. It then adds words at random and, for each word added, removes
    all possibilities that are now invalid, and updates the connected
    possibilities.
    This is done until the grid is above a given completion level.

    Return:
    This function returns a dictionary, in which ["grid"] is the grid, and
    "words" is the list of included words. The grid is a simple list of lists,
    where zeroes represent the slots that were not filled in, with the
    remaining slots containing a single letter each.

    Assumptions:
    Each possibility is a dictionary of the kind:
    p["word"] = the actual string
    p["location"] = the [i,j] (i is row and j is col) list with the location
    p["D"] = the direction of the possibility (E for ->, S for down)
    """
    print("Generating {} grid with {} words.".format(dim, len(words)))

    # Initialize grid
    grid = [x[:] for x in [[0]*dim[1]]*dim[0]]

    # Initialize the list of added words
    added_words = []
    added_strings = []

    # Draw a number of words from the dictionary and generate all possibilities
    sample = draw_words(words, 1000)
    possibilities = generate_possibilities(sample, dim)
    connected_possibilities = []

    # Add seed word (should be large)
    seed = possibilities.pop(random.randint(0, len(possibilities)-1))
    while len(seed["word"]) < 9:
        seed = possibilities.pop(random.randint(0, len(possibilities)-1))
    add_word_to_grid(seed, grid)
    print("Seed:")
    print(seed)

    # Fill in grid
    occupancy = 0
    # TODO: Add other limits: time, tries, no more words, etc
    while occupancy < 0.5:
        # Generate new possibilities, if needed
        while not connected_possibilities:
            print("Getting new words!", end=" ")
            sample = draw_words(words, 1200)
            possibilities.extend(generate_possibilities(sample, dim))
            possibilities = [x for x in possibilities if is_valid(x, grid) and x["word"] not in added_strings]
            # Update connected possibilities
            connected_possibilities = [x for x in possibilities if not is_disconnected(x, grid)]
            print("Possibilities: {}. Connected: {}.".format(len(possibilities), len(connected_possibilities)))

        # Add new possibility
        if connected_possibilities:
            new = connected_possibilities.pop(random.randint(0, len(connected_possibilities)-1))
        else:
            print("No connected possibilities!")
            new = possibilities.pop(random.randint(0, len(possibilities)-1))

        # Add word to grid and to the list of added words
        add_word_to_grid(new, grid)
        added_words.append(new)
        added_strings.append(new["word"])

        # Remove now-invalid possibilities and update connected possibilities
        possibilities = [x for x in possibilities if is_valid(x, grid) and x["word"] not in added_strings]
        connected_possibilities = [x for x in possibilities if not is_disconnected(x, grid)]

        # Update occupancy
        occupancy = 1 - (sum(x.count(0) for x in grid) / (dim[0]*dim[1]))
        print("Word added. Occupancy: {:2.3f}. Possibilities: {}. Connected: {}.".format(occupancy, len(possibilities), len(connected_possibilities)))

    # Report and return the grid
    print("Build a grid of occupancy {}.".format(occupancy))
    return {"grid": grid, "words": added_words}


def write_grid(grid, screen=False, out_file="table.tex", words=[]):
    """ This function receives the generated grid and writes it to the file (or
    to the screen, if that's what we want). The grid is expected to be a list
    of lists, as used by the remaining functions.

    If a list of words is given, it is taken as the words used on the grid and
    is printed as such.
    """
    if screen is True:
        # Print grid to the screen
        for line in grid:
            for element in line:
                print(" {}".format(element), end="")
            print()
    else:
        # Print grid to the file and compile
        with open(out_file, "w") as texfile:
            # Write preamble
            texfile.write("\documentclass[a4paper]{article}" + "\n")
            texfile.write(r"\usepackage[utf8]{inputenc}" + "\n")
            texfile.write(r"\usepackage[table]{xcolor}" + "\n")
            texfile.write(r"\usepackage{multicol}" + "\n")
            texfile.write(r"\usepackage{fullpage}" + "\n")
            texfile.write(r"\usepackage{graphicx}" + "\n")
            texfile.write("\n")
            texfile.write(r"\begin{document}" + "\n")
            texfile.write(r"\section*{Complete grid}" + "\n")

            # Resize box
            texfile.write(r"\resizebox{\textwidth}{!}{")

            # Write table environment and format
            texfile.write(r"\begin{tabular}{|")
            for i in range(len(grid[0])):
                texfile.write(r"c|")
            texfile.write("}\n\hline\n")

            # Write actual table
            for line in grid:
                for index, element in enumerate(line):
                    if element == 0:
                        texfile.write(r"\cellcolor{black}0")

                    # This feels a bit hacky, suggestions appreciated
                    if index != len(line)-1:
                        texfile.write(" & ")

                texfile.write(r"\\ \hline" + "\n")

            # End tabular environment
            texfile.write("\end{tabular}\n")
            texfile.write(r"}" + "\n\n")

            # Write the words that were used
            if words:
                texfile.write(r"\section*{Words used for the problem}" + "\n")
                # Write in several columns
                texfile.write(r"\begin{multicols}{4}" + "\n")
                texfile.write(r"\noindent" + "\n")
                # Sort words by size
                words.sort(key=lambda word: (len(word), word[0]))
                # Write words
                for word in words:
                    texfile.write(word + r"\\" + "\n")
                # End multicolumn environment
                texfile.write(r"\end{multicols}" + "\n")

            # Page break and new section
            texfile.write(r"\newpage" + "\n")
            texfile.write(r"\section*{Solution}" + "\n")

            # Write solution
            # Resize box
            texfile.write(r"\resizebox{\textwidth}{!}{")

            # Write table environment and format
            texfile.write(r"\begin{tabular}{|")
            for i in range(len(grid[0])):
                texfile.write(r"c|")
            texfile.write("}\n\hline\n")

            # Write actual table
            for line in grid:
                for index, element in enumerate(line):
                    if element == 0:
                        texfile.write(r"\cellcolor{black}0")
                    else:
                        texfile.write(str(element))
                    # This feels a bit hacky, suggestions appreciated
                    if index != len(line)-1:
                        texfile.write(" & ")

                texfile.write(r"\\ \hline" + "\n")

            # End tabular environment
            texfile.write("\end{tabular}\n")
            texfile.write(r"}")

            # End document
            texfile.write("\end{document}\n")

        # Compile in a temp folder
        # (inspired by
        # https://stackoverflow.com/questions/19683123/compile-latex-from-python)
        if not screen:
            print("\n=== Compiling the generated latex file! ===")
            with tempfile.TemporaryDirectory() as tmpdir:
                # Save current directory
                original_dir = os.getcwd()

                # Copy the latex source to the temporary directory
                shutil.copy(out_file, tmpdir)

                # Move to the temp directory
                os.chdir(tmpdir)

                # Rename .tex file to generic name "out"
                os.rename(out_file, "out.tex")

                # Compile
                proc = subprocess.call(['pdflatex', "out.tex"])

                # Copy PDF back to the original directory
                shutil.copy("out.pdf", original_dir)
            print("=== Done! ===\n")


if __name__ == "__main__":
    # Read words from file
    words = read_word_list("words.txt")

    # Generate grid
    grid = generate_grid(words, [20, 20])

    # Show grid
    print("Final grid:")
    write_grid(grid["grid"], screen=True)
    print("Words:")
    pprint.pprint(grid["words"])

    # Print to file and compile
    write_grid(grid["grid"], words=[x["word"] for x in grid["words"]])
