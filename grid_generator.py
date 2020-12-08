import basic_ops


class GridGenerator:
    def __init__(self, word_list, dimensions, n_loops, timeout, target_occupancy):
        self.word_list = word_list
        self.dimensions = dimensions
        self.n_loops = n_loops
        self.timeout = timeout
        self.target_occupancy = target_occupancy
        self.reset()

    def reset(self):
        self.grid = basic_ops.create_empty_grid(self.dimensions)
        self.words_in_grid = []

    def get_grid(self):
        return self.grid

    def get_words_in_grid(self):
        return self.words_in_grid

    def generate_grid(self):
        """ Updates the internal grid with content.
        """
        self.reset()
        print("Generating {} grid with {} words.".format(self.dimensions, len(self.word_list)))

        # Fill it up with the recommended number of loops
        for i in range(self.n_loops):
            print("Starting execution loop {}:".format(i+1))
            self.generate_content_for_grid()

            print("Culling isolated words.")
            self.cull_isolated_words()
            self.reset_grid_to_existing_words()

        print("Built a grid of occupancy {}.".format(basic_ops.compute_occupancy(self.grid)))

    def generate_content_for_grid(self):
        """ Uses the basic fill algorithm to fill up the crossword grid.
        """
        self.words_in_grid += basic_ops.basic_grid_fill(self.grid, self.target_occupancy, self.timeout, self.dimensions, self.word_list)

    def cull_isolated_words(self):
        """ Removes words that are too isolated from the grid

        TODO: does not seem to work correctly yet.
        """
        isolated_words = []

        for word in self.words_in_grid:
            if basic_ops.is_isolated(word, self.grid):
                print("Culling word: {}.".format(word))
                isolated_words.append(word)

        for word in isolated_words:
            self.words_in_grid.remove(word)

    def reset_grid_to_existing_words(self):
        """ Resets the stored grid to the words in self.words_in_grid
        """
        self.grid = basic_ops.create_empty_grid(self.dimensions)

        for word in self.words_in_grid:
            basic_ops.add_word_to_grid(word, self.grid)
