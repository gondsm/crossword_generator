Crossword Generator
===

This very simple Python script generates a *clueless* crossword puzzle. It harnesses the capabilities of Python and LaTeX to output the puzzle in a printable PDF.

Algorithm
---

I purposefully designed and implemented this little project without performing research on crossword generation techniques; I wanted to see if I could do it by myself. The very simple algorithm that is implemented here is as follows:

1. The technique receives a list of words, in a .txt file (I tested using [these](http://www.gwicks.net/dictionaries.htm) lists).
2. A number (1000, by default) of words are chosen randomly from the list that is given, and these are the words that will be used hereafter.
3. The technique expands the list of words into a list of possibilities, where each possibility encodes a possible starting location for a word, as well as its direction. This essentially constitutes all possible words that can be placed into the grid.
4. Words that connect to words that are already on the grid are isolated into a connected_possibilities list.
5. A new word is taken from the list of possibilities/connected_possibilities and placed on the grid. This makes it so a number of possibilities are now invalid, and these are removed from the list. Steps 3 through 5 are repeated until the grid is as full as we want it to be, or the script times out.

Output
---

The script depends on LaTeX for producing the PDF output. However, the grid can be (and is, by default) printed to the screen. The PDF is print-ready, and includes both the puzzle (with the needed words) and the solution, making the output of each run completely self-contained.


Performance Considerations
---

On my consumer-grade machine (i7-6700HQ) the algorithm can generate a 20x20 grid with 50% completion in some ~~45~~ 10 seconds (with the new algorithm). I am currently looking into ways of improving this mark, and already have a ton of ideas, so stay tuned!

Usage
---

For now (until I implement argparsing), all you have to do is run the script on a folder where a "words.txt" file with one word per line exists. I recommend using the aforementioned lists!
