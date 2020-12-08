import random
import time


def generate_random_possibility(words, dim):
    """ This function returns a randomly-generated possibility, instead of generating all
    possible ones.
    """
    # Generate possibility
    possibility = {"word": words[random.randint(0, len(words)-1)],
                   "location": [random.randint(0, dim[0]-1), random.randint(0, dim[1]-1)],
                   "D": "S" if random.random() > 0.5 else "E"}

    # Return it
    return possibility


def is_within_bounds(word_len, line, column, direction, grid_width, grid_height):
    """ Returns whether the given word is withing the bounds of the grid.
    """
    return (direction == "E" and column + word_len <= grid_width) or (direction == "S" and line + word_len <= grid_height)


def collides_with_existing_words(word, line, column, direction, grid):
    """ Returns whether the given word collides with an existing one.
    """
    for k, letter in enumerate(list(word)):
        if direction == "E":
            # Collisions
            if grid[line][column+k] != 0 and grid[line][column+k] != letter:
                return True
        if direction == "S":
            # Collisions
            if grid[line+k][column] != 0 and grid[line+k][column] != letter:
                return True

    return False


def ends_are_isolated(word, line, column, direction, grid):
    """ Returns whether the given word is isolated (blank before start and after end).
    """
    if direction == "E":
        # If the preceding space isn't empty
        if not is_cell_free(line, column-1, grid):
            return False
        # If the succeding space isn't empy
        if not is_cell_free(line, column+len(word), grid):
            return False
    if direction == "S":
        # If the preceding space isn't empty
        if not is_cell_free(line-1, column, grid):
            return False
        # If the succeding space isn't empy
        if not is_cell_free(line+len(word), column, grid):
            return False

    return True


def find_new_words(word, line, column, direction, grid, words):
    """ Given a new potential word, looks for new words that might have been created by adding it to the grid.

    Returns None if new words are (geometrically) created but are not valid.
    """
    new_words = []

    for k, letter in enumerate(list(word)):
        if direction == "E":
            # If the space was originally blank and there are adjacent letters
            if grid[line][column+k] == 0 and (line > 0 and grid[line-1][column+k] != 0 or line < len(grid)-1 and grid[line+1][column+k]):
                # Then we have to extract this new word
                poss_word = [letter]
                l = 1
                while line+l < len(grid[0]) and grid[line+l][column+k] != 0:
                    poss_word.append(grid[line+l][column+k])
                    l+=1
                l = 1
                while line-l > 0 and grid[line-l][column+k] != 0:
                    poss_word.insert(0, grid[line-l][column+k])
                    l+=1
                poss_word = ''.join(poss_word)

                # And check if it exists in the list
                if poss_word not in words:
                    return None

                new_words.append({"D": "S", "word":poss_word, "location": [line-l+1, column+k]})

        if direction == "S":
            # If the space was originally blank and there are adjacent letter
            if grid[line+k][column] == 0 and (column > 0 and grid[line+k][column-1] != 0 or column < len(grid[0])-1 and grid[line+k][column+1]):
                # Then we have to extract this new word
                poss_word  = [letter]
                l = 1
                while column+l < len(grid) and grid[line+k][column+l] != 0:
                    poss_word.append(grid[line+k][column+l])
                    l+=1
                l = 1
                while column-l > 0 and grid[line+k][column-l] != 0:
                    poss_word.insert(0, grid[line+k][column-l])
                    l+=1
                poss_word = ''.join(poss_word)

                # And check if it exists in the list
                if poss_word not in words:
                    return None

                new_words.append({"D": "E", "word":poss_word, "location": [line+k,column-l+1]})

    return new_words


def is_valid(possibility, grid, words):
    """ This function determines whether a possibility is still valid in the
    given grid. (see generate_grid)

    A possibility is deemed invalid if:
     -> it extends out of bounds
     -> it collides with any word that already exists, i.e. if any of its
     elements does not match the words already in the grid;
     -> if the cell that precedes and follows it in its direction is not empty.

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
    if not is_within_bounds(len(word), i, j, D, len(grid[0]), len(grid)):
        return False

    # Collisions
    if collides_with_existing_words(word, i, j, D, grid):
        return False

    # Start and End
    if not ends_are_isolated(word, i, j, D, grid):
        return False

    # If we can't find any issues, it must be okay!
    return True


def score_candidate(candidate_word, new_words):
    return len(candidate_word) + 10*len(new_words)


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


def select_candidate(candidates, scores):
    """ Select the candidate with the maximum score
    """
    max_score = max(scores)
    idx = scores.index(max_score)

    return candidates[idx], scores[idx]


def compute_occupancy(grid):
    return 1 - (sum(x.count(0) for x in grid) / (len(grid[0])*len(grid)))


def create_empty_grid(dimensions):
    """ Creates an empty grid with the given dimensions.

    dimensions[0] -> lines
    dimensions[1] -> columns
    """
    return [x[:] for x in [[0]*dimensions[1]]*dimensions[0]]


def generate_valid_candidates(grid, words, dim, timeout):
    # Generate new candidates
    candidates = []
    scores = []
    new_words = []
    tries = 0

    start_time = time.time()

    # Generate a new candidate
    while not candidates and time.time() < start_time + timeout:
        # Increment search "time"
        tries += 1

        # Get new possibility
        new = generate_random_possibility(words, dim)

        # Evaluate validity
        if not is_valid(new, grid, words):
            continue

        # Find new words that this possibility generates
        new_words = find_new_words(new["word"], new["location"][0], new["location"][1], new["D"], grid, words)

        # If new_words is None, then the possibility is invalid
        if new_words == None:
            new_words = []
            continue

        # Calculate this possibility's score
        score = score_candidate(new["word"], new_words)

        # Add to list of candidates
        candidates.append(new)
        scores.append(score)

    return candidates, scores, new_words


def is_cell_free(line, col, grid):
    """ Checks whether a cell is free.

    Does not throw if the indices are out of bounds. These cases return as free.
    """
    # Negative indices are "legal", but we treat them as out of bounds.
    if line < 0 or col < 0:
        return True

    try:
        return grid[line][col] == 0
    except IndexError:
        return True


def is_isolated(possibility, grid):
    """ Determines whether a given possibility is completely isolated in the given grid.

    It is assumed that the possibility is valid, of course.
    """
    # Import possibility to local vars, for clarity
    line = possibility["location"][0]
    column = possibility["location"][1]
    word = possibility["word"]
    direction = possibility["D"]

    # The word cannot be isolated if there is something at its ends
    if not ends_are_isolated(word, line, column, direction, grid):
        return False

    # Look at the cells that surround the word
    for i in range(len(word)):
        if direction == "E":
            if not is_cell_free(line-1, column+i, grid) or not is_cell_free(line+1, column+i, grid):
                return False
        if direction == "S":
            if not is_cell_free(line+i, column-1, grid) or not is_cell_free(line+i, column+1, grid):
                return False

    # If nothing was found, then the word is isolated
    return True


def basic_grid_fill(grid, occ_goal, timeout, dim, words):
    """ Actually finds valid possibilities, scores them and adds them to the grid.

    Algorithm:
    This function operates by taking the words it receives randomly generating possibilities
    until a valid one is found. It is then added to the grid.
    This is done until the grid is above a given completion level.
    """
    start_time = time.time()
    occupancy = 0
    added_words = []

    while occupancy < occ_goal and time.time() - start_time < timeout:
        # Generate some candidates
        # This is limited to 1/10 of the total time we can use.
        candidates, scores, new_words = generate_valid_candidates(grid, words, dim, timeout/10)

        # If there are no candidates, we move to the next iteration. This ensures that we can actually respect timeouts.
        if not candidates:
            continue

        # Select best candidate
        new, new_score = select_candidate(candidates, scores)

        # Add word to grid and to the list of added words
        add_word_to_grid(new, grid)
        added_words.append(new)

        # Add new words to the words list
        for word in new_words:
            added_words.append(word)

        # Remove words from list so we don't repeat ourselves
        words.remove(new["word"])
        for word in new_words:
            words.remove(word["word"])

        # Update occupancy
        occupancy = compute_occupancy(grid)
        print("Word \"{}\" added. Occupancy: {:2.3f}. Score: {}.".format(new["word"], occupancy, new_score))
        if new_words:
            print("This also created the words:", new_words)

    return added_words