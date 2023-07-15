"""
6.1010 Spring '23 Lab 8: SAT Solver
"""

#!/usr/bin/env python3

import sys
import typing
import doctest

sys.setrecursionlimit(10_000)
# NO ADDITIONAL IMPORTS


def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) 
    is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    if formula == []:
        return {}
    
    new_formula = list(formula)
    new_formula.sort(key=len)

    for clause in new_formula:
        if clause == []:
            return None
        if len(clause) == 1:
            new_formula = update(new_formula, clause[0][0], clause[0][1])
            new_assignment = satisfying_assignment(new_formula)
            if new_assignment is None:
                return None
            new_assignment[clause[0][0]] = clause[0][1]
            return new_assignment
    
    for clause in formula:
        for literal in clause:
            variable = literal[0]
            true_formula = update(new_formula, variable, True)
            true_assignment = satisfying_assignment(true_formula)
            if true_assignment is not None:
                true_assignment[variable] = True
                return true_assignment
            false_formula = update(new_formula, variable, False)
            false_assignment = satisfying_assignment(false_formula)
            if false_assignment is not None:
                false_assignment[variable] = False
                return false_assignment
            return None

def update(formula, variable, value):
    """
    update formula based on setting variable to value
    """
    new_formula = list(formula)
    clauses_to_remove = []

    for i, clause in enumerate(new_formula):
        delete_clause = False
        for literal in clause:
            if variable == literal[0]:
                if value == literal[1]:
                    delete_clause = True
                    break
        if delete_clause:
            clauses_to_remove.append(clause)
        else:
            new_formula[i] = [literal for literal in clause if variable != literal[0]]

    for clause in clauses_to_remove:
        new_formula.remove(clause)

    return new_formula


def sudoku_board_to_sat_formula(sudoku_board):
    """
    Generates a SAT formula that, when solved, represents a solution to the
    given sudoku board.  The result should be a formula of the right form to be
    passed to the satisfying_assignment function above.
    """
    n = len(sudoku_board)
    p = int(n**0.5)
    formula = []

    formula += restrictions(sudoku_board, n, p)

    formula += rows_and_cols(n)

    formula += subgrids(n)

    formula += no_same(n)

    return formula

def restrictions(sudoku_board, n, p):
    """
    Create clauses based on already filled-in info.
    """
    formula = []

    for row in range(n):
        for col in range(n):
            val = sudoku_board[row][col]
            if val != 0:
                formula += restriction(sudoku_board, row, col, val, n, p)

    return formula

def restriction(sudoku_board, row, col, val, n, p):
    formula = []

    formula.append([((row, col, val), True)])
    for i in range(n):
        if i != col and sudoku_board[row][i] == 0:
            formula.append([((row, i, val), False)])
        if i != row and sudoku_board[i][col] == 0:
            formula.append([((i, col, val), False)])
    min_row = int(row - row % p)
    max_row = min_row + p
    min_col = int(col - col % p)
    max_col = min_col + p
    for subgrid_row in range(min_row, max_row):
        for subgrid_col in range(min_col, max_col):
            if (
                subgrid_row != row
                and subgrid_col != col
                and sudoku_board[subgrid_row][subgrid_col] == 0
            ):
                formula.append([((subgrid_row, subgrid_col, val), False)])

    return formula

def rows_and_cols(n):
    """
    Create the clauses corresponding to every number in every 
    row and column, no number in row or column twice.
    """
    formula = []
    for i in range(n):
        for j in range(1, n + 1):
            i_row_clause = []
            i_col_clause = []
            for k in range(n):
                i_row_clause.append(((i, k, j), True))
                i_col_clause.append(((k, i, j), True))
            formula.append(i_row_clause)
            formula.append(i_col_clause)
            for k in range(n - 1):
                for r in range(k + 1, n):
                    formula.append([((i, k, j), False), ((i, r, j), False)])
                    formula.append([((k, i, j), False), ((r, i, j), False)])
    return formula


def subgrids(n):
    """
    Create clauses corresponding to every number in each grid.
    """
    p = int(n**0.5)
    formula = []
    for i in range(p):
        for _ in range(p):
            for k in range(1, n + 1):
                ij_clause = []
                squares = []
                for r in range(i * p, (i + 1) * p):
                    for c in range(i * p, (i + 1) * p):
                        ij_clause.append(((r, c, k), True))
                        squares.append((r, c))
                formula.append(ij_clause)
                for a in range(n-1):
                    for b in range(a+1, n):
                        formula.append([((squares[a][0], squares[a][1], k), False), ((squares[b][0], squares[b][1], k), False)])
    return formula


def no_same(n):
    formula = []
    for i in range(n):
        for j in range(n):
            for k in range(1, n):
                for m in range(k + 1, n + 1):
                    formula.append([((i, j, k), False), ((i, j, m), False)])
    return formula


def assignments_to_sudoku_board(assignments, n):
    """
    Given a variable assignment as given by satisfying_assignment, as well as a
    size n, construct an n-by-n 2-d array (list-of-lists) representing the
    solution given by the provided assignment of variables.

    If the given assignments correspond to an unsolvable board, return None
    instead.
    """
    if assignments is None:
        return None

    cells = set(assignments.keys())
    board = [[0 for _ in range(n)] for _ in range(n)]
    for row in range(n):
        for col in range(n):
            no_assignment = True
            for i in range(1, n + 1):
                if (row, col, i) in cells:
                    if assignments[(row, col, i)]:
                        board[row][col] = i
                        no_assignment = False
                        break
            if no_assignment:
                return None
    return board


if __name__ == "__main__":
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
    # doctest.run_docstring_examples(
    #     satisfying_assignment,
    #     globals(),
    #     # optionflags=_doctest_flags,
    #     verbose=True,)
    cnf = [
        [["a", True], ["a", False]],
        [["b", True], ["a", True]],
        [["b", True]],
        [["b", False], ["b", False], ["a", False]],
        [["c", True], ["d", True]],
        [["c", True], ["d", True]],
    ]
    print(satisfying_assignment(cnf))
