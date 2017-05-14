#!/usr/bin/python3
""" Crossword Generator

This script takes a list of words and creates a new latex table representing a
crosswod puzzle, which is then printed to PDF, and can be printed to actual
paper, if you're one of those people.
"""

# STL imports
import random
import pprint
import subprocess
import tempfile
import os
import shutil
import time
import argparse


# Auxiliary Functions
def generate_single_possibility(words, dim):
    """ This function returns a randomly-generated possibility, instead of generating all
    possible ones.
    """
    # Generate possibility
    possibility = {"word": words[random.randint(0, len(words)-1)],
                   "location": [random.randint(0, dim[0]-1), random.randint(0, dim[1]-1)],
                   "D": "S" if random.random() > 0.5 else "E"}

    # Return it
    return possibility


def is_valid(possibility, grid, words):
    """ This function determines whether a possibility is still valid in the
    given grid. (see generate_grid)

    A possibility is deemed invalid if:
     -> it extends out of bounds
     -> it collides with any word that already exists, i.e. if any of its
     elements does not match the words already in the grid;
     -> if the cell that precedes and succedes it in its direction is not empty.

    The function also analyses how the word interacts with previous adjacent
    words, and invalidates the possibility of returns a list with the new
    words, if applicable.
    """
    # Import possibility to local vars, for clarity
    i = possibility["location"][0]
    j = possibility["location"][1]
    word = possibility["word"]
    D = possibility["D"]

    # Boundaries
    if (D == "E" and j + len(word) > len(grid[0])) or (D == "S" and i + len(word) > len(grid)):
        return [False, []]

    # Collisions
    for k, letter in enumerate(list(word)):
        if D is "E":
            # Collisions
            if grid[i][j+k] != 0 and grid[i][j+k] != letter:
                return [False, []]
        if D is "S":
            # Collisions
            if grid[i+k][j] != 0 and grid[i+k][j] != letter:
                return [False, []]

    # Start and End
    if D is "E":
        # If the preceding space isn't empty
        if j > 0 and grid[i][j-1] != 0:
            return [False, []]
        # If the succeding space isn't empy
        if j+len(word) < len(grid[0]) and grid[i][j+len(word)] != 0:
            return [False, []]
    if D is "S":
        # If the preceding space isn't empty
        if i > 0 and grid[i-1][j] != 0:
            return [False, []]
        # If the succeding space isn't empy
        if i+len(word) < len(grid) and grid[i+len(word)][j] != 0:
            return [False, []]

    # Detect if new words are formed
    new_words = []
    for k, letter in enumerate(list(word)):
        if D is "E":
            # If the space was originally blank and there are adjacent letters
            if grid[i][j+k] == 0 and (i > 0 and grid[i-1][j+k] != 0 or i < len(grid)-1 and grid[i+1][j+k]):
                # Then we have to extract this new word
                poss_word  = [letter]
                l = 1
                while i+l < len(grid[0]) and grid[i+l][j+k] != 0:
                    poss_word.append(grid[i+l][j+k])
                    l+=1
                l = 1
                while i-l > 0 and grid[i-l][j+k] != 0:
                    poss_word.insert(0, grid[i-l][j+k])
                    l+=1
                poss_word = ''.join(poss_word)
                # And check if it exists in the list
                if poss_word not in words:
                    return [False, []]
                new_words.append({"D": "S", "word":poss_word, "location": [i-l+1,j+k]})
        if D is "S":
            # If the space was originally blank and there are adjacent letter
            if grid[i+k][j] == 0 and (j > 0 and grid[i+k][j-1] != 0 or j < len(grid[0])-1 and grid[i+k][j+1]):
                # Then we have to extract this new word
                poss_word  = [letter]
                l = 1
                while j+l < len(grid) and grid[i+k][j+l] != 0:
                    poss_word.append(grid[i+k][j+l])
                    l+=1
                l = 1
                while j-l > 0 and grid[i+k][j-l] != 0:
                    poss_word.insert(0, grid[i+k][j-l])
                    l+=1
                poss_word = ''.join(poss_word)
                # And check if it exists in the list
                if poss_word not in words:
                    return [False, []]
                new_words.append({"D": "E", "word":poss_word, "location": [i+k,j-l+1]})

    # If we can't find any issues, it must be okay!
    return [True, new_words]


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


# Grid generation
def generate_grid(words, dim, timeout=60, occ_goal=0.9):
    """ This function receives a list of words and creates a new grid, which
    represents our puzzle. The newly-created grid is of dimensions
    dim[0] * dim[1] (rows * columns). The function also receives a timeout,
    which is used to control the time-consuming section of the code. If the
    timeout is reached, the functions returns the best grid it was able to
    achieve thus far. Lastly, occ_goal represents the fraction of squares that
    should be, ideally, filled in.

    Algorithm:
    This function operates by taking the words it receives randomly generating possibilities
    until a valid one is found. It is then added to the grid.
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

    # Initialize time structure and occupancy
    start_time = time.time()
    occupancy = 0

    # Main loop
    while occupancy < occ_goal and time.time() - start_time < timeout:
        # Generate new candidates (think tournament selection)
        candidates = []
        i = 0
        # While we don't have any, or we have and have been searching for a short time
        new_words = []
        while not candidates or (candidates and i < 100):
            valid = False
            # Generate a new candidate
            while not valid:
                # Get new possibility
                new = generate_single_possibility(words, dim)
                # Evaluate validity and get new words generated
                valid, new_words = is_valid(new, grid, words)
                # Increment search "time"
                i += 1
            # Add to list of candidates
            candidates.append(new)

        # Sort candidates by length
        candidates = sorted(candidates, key=lambda k: len(k['word']), reverse=True)
        new = candidates[0]
        # Get possible words generated by new candidate
        # TODO: improve this crap
        valid, new_words = is_valid(new, grid, words)

        # Add word to grid and to the list of added words
        add_word_to_grid(new, grid)
        added_words.append(new)

        # Add new words to the words list
        for word in new_words:
            added_words.append(word)

        # Remove words from list
        words.remove(new["word"])
        for word in new_words:
            words.remove(word["word"])

        # Update occupancy
        occupancy = 1 - (sum(x.count(0) for x in grid) / (dim[0]*dim[1]))
        print("Word \"{}\" added. Occupancy: {:2.3f}.".format(new["word"],occupancy))
        if new_words:
            print("This also created the words:", new_words)

    # Report and return the grid
    print("Built a grid of occupancy {}.".format(occupancy))
    return {"grid": grid, "words": added_words}


def write_grid(grid, screen=False, out_file="table.tex", out_pdf="out.pdf", keep_tex=False, words=[]):
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
            texfile.write(r"\section*{Challenge}" + "\n")

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
                shutil.copy("out.pdf", original_dir+"/"+out_pdf)

                # Move back to the original directory
                os.chdir(original_dir)
            print("=== Done! ===\n")

        # Remove tex file?
        if not keep_tex:
            os.remove(out_file)


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description='Generate a crossword puzzle.')
    parser.add_argument('-f', type=str,
                        default="words.txt",
                        dest="word_file",
                        help="A file containing words, one word per line.")
    parser.add_argument('-d', type=int,
                        nargs="+",
                        default=[20, 20],
                        dest="dim",
                        help="Dimensions of the grid to build.")
    parser.add_argument('-t', type=int,
                        default=10,
                        dest="timeout",
                        help="Maximum execution time, in seconds.")
    parser.add_argument('-o', type=float,
                        default=0.9,
                        dest="target_occ",
                        help="Minimum desired occupancy of the final grid.")
    parser.add_argument('-p', type=str,
                        default="out.pdf",
                        dest="out_pdf",
                        help="Name of the output pdf file.")
    args = parser.parse_args()

    # Read words from file
    words = read_word_list(args.word_file)

    # Filter small words
    words = [x for x in words if len(x) > 2]

    # Generate grid
    dim = args.dim if len(args.dim)==2 else [args.dim[0], args.dim[0]]
    print("Making a grid of dimension {}, in {} seconds with a target occupancy of {}.".format(dim, args.timeout, args.target_occ))
    grid = generate_grid(words, dim, timeout=args.timeout, occ_goal=args.target_occ)

    # Print to file and compile
    write_grid(grid["grid"], words=[x["word"] for x in grid["words"]], out_pdf=args.out_pdf)

    # Show grid
    print("Final grid:")
    write_grid(grid["grid"], screen=True)
    print("Words:")
    pprint.pprint(grid["words"])