"""
6.1010 Spring '23 Lab 7: Mines
"""

#!/usr/bin/env python3

import typing
import doctest

# NO ADDITIONAL IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f"{key}:")
            for inner in val:
                print(f"    {inner}")
        else:
            print(f"{key}:", val)


# 2-D IMPLEMENTATION


def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'hidden' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    hidden:
        [True, True, True, True]
        [True, True, True, True]
    state: ongoing
    """
    return new_game_nd((num_rows, num_cols), bombs)


def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['hidden'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is revealed on the board after digging (i.e. game['hidden'][bomb_location]
    == False), 'victory' when all safe squares (squares that do not contain a
    bomb) and no bombs are revealed, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden': [[True, False, True, True],
    ...                  [True, True, True, True]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    hidden:
        [True, False, False, False]
        [True, True, False, False]
    state: victory

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden': [[True, False, True, True],
    ...                  [True, True, True, True]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    hidden:
        [False, False, True, True]
        [True, True, True, True]
    state: defeat
    """
    return dig_nd(game, (row, col))


def render_2d_locations(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  game['hidden'] indicates which squares should be hidden.  If
    xray is True (the default is False), game['hidden'] is ignored and all
    cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the that are not
                    game['hidden']

    Returns:
       A 2D array (list of lists)

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden':  [[True, False, False, True],
    ...                   [True, True, False, True]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden':  [[True, False, True, False],
    ...                   [True, True, True, False]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    return render_nd(game, xray)


def render_2d_board(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['hidden']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'hidden':  [[False, False, False, True],
    ...                            [True, True, False, True]]})
    '.31_\\n__1_'
    """
    rendered_locations = render_2d_locations(game, xray)
    rendered_board = ""

    for i, row in enumerate(rendered_locations):
        row_str = "".join(row)
        if i != len(rendered_locations) - 1:
            row_str += "\n"
        rendered_board += row_str

    return rendered_board


# N-D IMPLEMENTATION


def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'hidden' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of tuples, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    hidden:
        [[True, True], [True, True], [True, True], [True, True]]
        [[True, True], [True, True], [True, True], [True, True]]
    state: ongoing
    """
    all_coords = get_all_coords(dimensions)
    board = starter_nd_board(dimensions, ".")
    hidden = starter_nd_board(dimensions, True)
    bomb_set = set(bombs)

    # for bomb_coord in bombs:
    #     set_cell(board, bomb_coord, ".")

    for coord in all_coords:
        if coord not in bomb_set:
            num_bombs = 0
            neighbors = get_neighbors(coord, dimensions)
            for neighbor in neighbors:
                if neighbor in bomb_set:
                    num_bombs += 1
            set_cell(board, coord, num_bombs)

    return {
        "board": board,
        "dimensions": dimensions,
        "hidden": hidden,
        "state": "ongoing",
    }


def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the hidden to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is revealed on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are revealed, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'hidden': [[[True, True], [True, False], [True, True],
    ...                [True, True]],
    ...               [[True, True], [True, True], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    hidden:
        [[True, True], [True, False], [False, False], [False, False]]
        [[True, True], [True, True], [False, False], [False, False]]
    state: ongoing
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'hidden': [[[True, True], [True, False], [True, True],
    ...                [True, True]],
    ...               [[True, True], [True, True], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    hidden:
        [[True, False], [True, False], [True, True], [True, True]]
        [[True, True], [True, True], [True, True], [True, True]]
    state: defeat
    """
    board = game["board"]
    hidden = game["hidden"]
    dimensions = game["dimensions"]

    if (
        game["state"] == "defeat"
        or game["state"] == "victory"
        or not get_cell(hidden, coordinates)
    ):
        return 0

    # if you reveal a bomb, then defeat
    # elif get_cell(board, coordinates) == ".":
    #     set_cell(hidden, coordinates, False)
    #     game["state"] = "defeat"
    #     return 1

    # bfs to find number of revealed squares
    else:
        set_cell(hidden, coordinates, False)
        if get_cell(board, coordinates) == ".":
            game["state"] = "defeat"
            return 1
        else:
            revealed = {coordinates}
            agenda = [coordinates]
            while agenda:
                current_cell = agenda.pop(0)
                if get_cell(board, current_cell) == 0:
                    for neighbor in get_neighbors(current_cell, dimensions):
                        if get_cell(hidden, neighbor) and neighbor not in revealed:
                            set_cell(hidden, neighbor, False)
                            revealed.add(neighbor)
                            agenda.append(neighbor)

            # victory check (all non-bomb squares all revealed)
            game["state"] = "victory"
            for coord in get_all_coords(dimensions):
                if get_cell(board, coord) != "." and get_cell(hidden, coord):
                    game["state"] = "ongoing"
                    break
            
            return len(revealed)


def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  The game['hidden'] array indicates which squares should be
    hidden.  If xray is True (the default is False), the game['hidden'] array
    is ignored and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['hidden']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'hidden': [[[True, True], [True, False], [False, False],
    ...                [False, False]],
    ...               [[True, True], [True, True], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    board = game["board"]
    hidden = game["hidden"]
    dimensions = game["dimensions"]

    def render(board, hidden, dimensions, xray):
        if len(dimensions) == 1:
            rendered = []
            for coord, cell_val in enumerate(board):
                if not xray and hidden[coord]:
                    rendered.append("_")
                elif cell_val != 0:
                    rendered.append(str(cell_val))
                else:
                    rendered.append(" ")
            return rendered
        else:
            return [
                render(board[i], hidden[i], dimensions[1:], xray)
                for i in range(len(board))
            ]

    return render(board, hidden, dimensions, xray)


def get_neighbors(x, dim):
    """
    get a list of all neighboring coordinates given a
    set of coordinates and the dimensions of the board
    """

    def neighbors_with_x(x, dim):
        """
        gets a list of the given coordinate and the coordinate itself
        """
        new_neighbors = []
        for coord in [x[0] - 1, x[0], x[0] + 1]:
            if 0 <= coord < dim[0]:
                new_neighbors.append((coord,))
        if len(dim) == 1:
            return new_neighbors
        else:
            return [
                a + b for a in new_neighbors for b in neighbors_with_x(x[1:], dim[1:])
            ]

    neighbors = neighbors_with_x(x, dim)
    neighbors.remove(x)

    return neighbors


def starter_nd_board(dim, x):
    """
    creates a board with specified dimensions, and every value is specified value
    """
    if len(dim) == 1:
        return [x for _ in range(dim[0])]
    else:
        return [starter_nd_board(dim[1:], x) for _ in range(dim[0])]


def get_cell(board, coord):
    """
    gets value in board at given coord
    """
    if len(coord) == 1:
        return board[coord[0]]
    else:
        row = get_cell(board, coord[:-1])
        return row[coord[-1]]


def set_cell(board, coord, val):
    """
    sets value in board at given coord to val
    """
    if len(coord) == 1:
        board[coord[0]] = val
    else:
        row = get_cell(board, coord[:-1])
        row[coord[-1]] = val


def get_all_coords(dim):
    """
    get all possible board coordinates given the dimensions of the board
    """
    if len(dim) == 1:
        return [(val,) for val in range(dim[0])]
    else:
        return [a + (b,) for a in get_all_coords(dim[:-1]) for b in range(dim[-1])]


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    # _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    # doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #
    doctest.run_docstring_examples(
        render_2d_board,
        globals(),
        # optionflags=_doctest_flags,
        verbose=True,
    )
    # game = {'board': [[0, 0, 1, '.', 1, 0], [0, 1, 2, 2, 1, 0],
    # [0, 1, '.', 1, 0, 0], [0, 1, 1, 1, 0, 0]],
    #   'dimensions': (4, 6), 'hidden': [[True, True, True, True,
    # False, False], [True, True, True, False, False, False],
    #                                    [True, True, True, False,
    # False, False], [True, True, True, False, False, False]], 'state': 'ongoing'}
    # coordinates = (0,5)
    # print(dig_2d(game, coordinates[0], coordinates[1]))
    # g = {'dimensions': (2, 4, 2),
    #      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    #                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    #     'hidden': [[[True, True], [True, False], [False, False], [False, False]],
    #                [[True, True], [True, True], [False, False], [False, False]]],
    #     'state': 'ongoing'}
    # print(render_nd(g, False))
    # print(render_nd(g, True))
    # print(render_2d_locations({'dimensions': (2, 4), 'state': 'ongoing',
    #                            'board': [['.', 3, 1, 0],
    #                                      ['.', '.', 1, 0]],
    #                             'hidden':  [[False, False, False, True],
    #                                         [True, True, False, True]]}))
