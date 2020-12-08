Crossword Generator
===

This very simple Python script generates a *clueless* crossword puzzle. It harnesses the capabilities of Python and LaTeX to output the puzzle in a printable PDF.

Usage
---

All you have to do is run the script on a folder where a "words.txt" file with one word per line exists. I recommend using the aforementioned lists! Run `./crossword_generator -h` to see all available options.

Output
---

The script depends on LaTeX for producing the PDF output. However, the grid can be (and is, by default) printed to the screen. The PDF is print-ready, and includes both the puzzle (with the needed words) and the solution, making the output of each run completely self-contained.

Performance Considerations
---

On my consumer-grade machine (i7-6700HQ) the algorithm can generate a 20x20 grid with 50% completion in some ~~45~~ ~~10~~ ~~4~~ seconds (with the new algorithm). I am currently looking into ways of improving this mark, and already have a ton of ideas, so stay tuned!

Algorithms
---

I purposefully designed and implemented this little project without performing research on crossword generation techniques; I wanted to see if I could do it by myself. I am essentially using this project as a testbench of sorts for coming up with search algorithms.

The basic algorithm currently in use essentially

1. Fills up the grid with random words in random positions, as long as they fit and do not collide;
2. Removes any isolated words, i.e. words that do not touch any others;
3. Repeats step 1.

This can be done ad infinitum. However, the time it takes to find valid possibilities scales exponentially with how full the grid already is, so getting past 60% occupancy takes quite a while.
