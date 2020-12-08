#!/usr/bin/python3
""" Crossword Generator

This script takes a list of words and creates a new latex table representing a
crossword puzzle, which is then printed to PDF. You can then print it to actual
paper, if you're one of those people.
"""

# Standard imports
import argparse

# Custom imports
import file_ops
import grid_generator
from grid_generator import GridGenerator


def parse_cmdline_args():
    """ Uses argparse to get commands line args.
    """
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
    parser.add_argument('-n', type=int,
                        default=1,
                        dest="n_loops",
                        help="NUmber of execution loops to run.")
    parser.add_argument('-t', type=int,
                        default=10,
                        dest="timeout",
                        help="Maximum execution time, in seconds, per execution loop.")
    parser.add_argument('-o', type=float,
                        default=0.9,
                        dest="target_occ",
                        help="Desired occupancy of the final grid.")
    parser.add_argument('-p', type=str,
                        default="out.pdf",
                        dest="out_pdf",
                        help="Name of the output pdf file.")
    return parser.parse_args()


if __name__ == "__main__":
    # Parse command line
    args = parse_cmdline_args()

    # Read words from file
    words = file_ops.read_word_list(args.word_file)
    print("Read {} words from file.".format(len(words)))

    # Construct the generator object
    dim = args.dim if len(args.dim)==2 else [args.dim[0], args.dim[0]]
    generator = GridGenerator(words, dim, args.n_loops, args.timeout, args.target_occ)

    # Generate the grid
    generator.generate_grid()

    # Write it out
    grid = generator.get_grid()
    words_in_grid = generator.get_words_in_grid()
    file_ops.write_grid_to_file(grid, words=[x["word"] for x in words_in_grid], out_pdf=args.out_pdf)
    file_ops.write_grid_to_screen(grid, words_in_grid)
