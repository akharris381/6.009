"""
6.1010 Spring '23 Lab 4: Snekoban Game
"""

import json
import typing

# NO ADDITIONAL IMPORTS!


direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    height = len(level_description)
    width = len(level_description[0])
    player_loc = None
    wall_set = set()
    comp_set = set()
    target_set = set()
    for i in range(height):
        for j in range(width):
            if "player" in level_description[i][j]:
                player_loc = (i, j)
            if "wall" in level_description[i][j]:
                wall_set.add((i, j))
            if "computer" in level_description[i][j]:
                comp_set.add((i, j))
            if "target" in level_description[i][j]:
                target_set.add((i, j))

    return (
        height,
        width,
        frozenset(wall_set),
        frozenset(comp_set),
        frozenset(target_set),
        player_loc,
    )


def victory_check(game):
    """
    Given a game representation (of the form returned from new_game), return
    a Boolean: True if the given game satisfies the victory condition, and
    False otherwise.
    """

    if game[3] == game[4] and game[3] != frozenset():
        return True

    return False


def new_location(location, direction):
    location_change = direction_vector[direction]
    return (location[0] + location_change[0], location[1] + location_change[1])


def step_game(game, direction):
    """
    Given a game representation (of the form returned from new_game), return a
    new game representation (of that same form), representing the updated game
    after running one step of the game.  The user's input is given by
    direction, which is one of the following: {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    computers = game[3]
    old_loc = game[5]
    new_loc = new_location(old_loc, direction)
    if new_loc in game[2]:
        return game
    elif new_loc in computers:
        new_comp_loc = new_location(new_loc, direction)
        if new_comp_loc in computers or new_comp_loc in game[2]:
            return game
        else:
            new_computers = set(computers)
            new_computers.remove(new_loc)
            new_computers.add(new_comp_loc)
            return (
                game[0],
                game[1],
                game[2],
                frozenset(new_computers),
                game[4],
                new_loc,
            )

    return (game[0], game[1], game[2], computers, game[4], new_loc)


def dump_game(game):
    """
    Given a game representation (of the form returned from new_game), convert
    it back into a level description that would be a suitable input to new_game
    (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    next_game = []
    height = game[0]
    width = game[1]

    for i in range(height):
        row = []
        for j in range(width):
            cell = []
            if game[5] == (i, j):
                cell.append("player")
            if (i, j) in game[2]:
                cell.append("wall")
            if (i, j) in game[3]:
                cell.append("computer")
            if (i, j) in game[4]:
                cell.append("target")
            row.append(cell)
        next_game.append(row)

    return next_game


def get_neighbors(game):
    return {step_game(game, direction) for direction in direction_vector}


def find_connecting_move(game1, game2):
    for direction in direction_vector:
        if step_game(game1, direction) == game2:
            return direction


def find_connecting_games(game):
    """
    Returns lists of game states in solution path starting from game and 
    ending at the victory state. Returns None if no solution exists.
    """
    if victory_check(game):
        return [game]
    agenda = [[game]]
    visited = {game}
    while agenda:
        current_path = agenda.pop(0)
        end_of_path = current_path[-1]
        for neighbor in get_neighbors(end_of_path):
            if neighbor not in visited:
                new_path = current_path + [neighbor]
                if victory_check(neighbor):
                    return new_path
                agenda.append(new_path)
                visited.add(neighbor)
    return None


def solve_puzzle(game):
    """
    Given a game representation (of the form returned from new game), find a
    solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    path = find_connecting_games(game)
    if path is None:
        return None
    solution = []
    pairs = zip(path, path[1:])
    for pair in pairs:
        solution.append(find_connecting_move(pair[0], pair[1]))
    return solution


if __name__ == "__main__":
    pass
