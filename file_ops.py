import os
import pprint
import shutil
import subprocess
import tempfile


def read_word_list(filename, min_length=2, min_different_letters=2):
    """ This function reads the file and returns the words read. It expects a
    file where each word is in a line.
    """
    # Initialize words list
    words = []

    # Get all the words
    with open(filename, encoding='latin1') as words_file:
        for line in words_file:
            word = line.strip()
            if len(word) > min_length and len(set(word)) > min_different_letters:
                words.append(word)

    # and we're done
    return words


def write_grid_to_file(grid, out_file="table.tex", out_pdf="out.pdf", keep_tex=False, words=[]):
    """ This function receives the generated grid and writes it to the file (or
    to the screen, if that's what we want). The grid is expected to be a list
    of lists, as used by the remaining functions.

    If a list of words is given, it is taken as the words used on the grid and
    is printed as such.
    """
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
    # (inspired by https://stackoverflow.com/questions/19683123/compile-latex-from-python)
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


def write_grid_to_screen(grid, words_in_grid):
    # Print grid to the screen
    print("Final grid:")
    for line in grid:
        for element in line:
            print(" {}".format(element), end="")
        print()

    print("Words:")
    pprint.pprint(words_in_grid)