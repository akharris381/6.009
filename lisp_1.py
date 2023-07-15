"""
6.1010 Spring '23 Lab 11: LISP Interpreter Part 1
"""
#!/usr/bin/env python3

import sys
import doctest

sys.setrecursionlimit(20_000)

# NO ADDITIONAL IMPORTS!

#############################
# Scheme-related Exceptions #
#############################


class SchemeError(Exception):
    """
    A type of exception to be raised if there is an error with a Scheme
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class SchemeSyntaxError(SchemeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class SchemeNameError(SchemeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class SchemeEvaluationError(SchemeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SchemeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(value):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Scheme
                      expression
    """
    if source == "":
        return []
    first = source[0]
    if first in {"(", ")"}:
        return [first] + tokenize(source[1:])
    elif first == ";":
        new_line = source.find("\n")
        if new_line == -1:
            return []
        return tokenize(source[new_line + 1 :])
    elif first in {" ", "\n"}:
        return tokenize(source[1:])
    end = 1
    while end < len(source) and (source[end] not in {" ", "(", ")", "\n", ";"}):
        end += 1
    return [source[:end]] + tokenize(source[end:])


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    if tokens.count("(") != tokens.count(")"):
        raise SchemeSyntaxError("number of open and close parentheses differ")
    if len(tokens) > 1 and tokens[-1] != ")":
        raise SchemeSyntaxError("expression not closed")

    def parse_expression(index):
        char = tokens[index]
        if char != "(":
            if char == ")":
                raise SchemeSyntaxError("misplaced )")
            return number_or_symbol(char), index
        sub_exp = []
        end = index
        while tokens[end + 1] != ")":
            next_sub, end = parse_expression(end + 1)
            sub_exp.append(next_sub)
        return sub_exp, end + 1

    return parse_expression(0)[0]


######################
# Built-in Functions #
######################
def product(args):
    if len(args) == 1:
        return args[0]
    return args[0] * product(args[1:])


def quotient(args):
    if len(args) == 1:
        return args[0]
    return quotient(args[:-1]) / args[-1]


scheme_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": product,
    "/": quotient,
}


class Frame:
    """
    Frame class. Instances have a parent and
    bindings for variables and functions.
    """

    def __init__(self, parent=None):
        self.parent = parent
        self.bindings = {}

    def __setitem__(self, var, val):
        self.bindings[var] = val

    def __getitem__(self, var):
        return (
            self.bindings[var] if var in self.bindings else self.parent.__getitem__(var)
        )

    def __contains__(self, var):
        if var in self.bindings:
            return True
        elif self.parent is not None:
            return self.parent.__contains__(var)
        return False


built_in_frame = Frame()
built_in_frame.bindings = scheme_builtins


class Function:
    def __init__(self, body, params, frame):
        self.body = body
        self.params = params
        self.frame = frame


##############
# Evaluation #
##############


def evaluate(tree, frame=None):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if frame is None:
        frame = Frame(built_in_frame)
    if isinstance(tree, str):
        return evaluate_string(tree, frame)
    elif isinstance(tree, (int, float)):
        return tree
    else:
        first = evaluate(tree[0], frame)
        if first in scheme_builtins.values():
            return first([evaluate(item, frame) for item in tree[1:]])
        elif first in {"lambda", "define"}:
            var = tree[1]
            val = tree[2]
            if first == "define":
                return define(frame, var, val)
            if first == "lambda":
                return Function(val, var, frame)
        elif isinstance(first, Function):
            return evaluate_function(first, tree, frame)
        raise SchemeEvaluationError(f"{first} is not a valid function")


def evaluate_string(tree, frame):
    if isinstance(tree, str):
        if tree in {"lambda", "define"}:
            return tree
        elif tree in frame:
            return frame[tree]
        else:
            raise SchemeNameError(f"{tree} not in frame")


def define(frame, var, val):
    if isinstance(val, str) and val not in frame:
        raise SchemeNameError(f"{val} not in frame")
    if isinstance(var, list):
        params = var[1:]
        var = var[0]
        val = ["lambda", params, val]
    frame[var] = evaluate(val, frame)
    return frame[var]


def evaluate_function(function, tree, frame):
    new_frame = Frame(function.frame)
    params = tree[1:]
    if len(params) != len(function.params):
        raise SchemeEvaluationError(
            f"wrong number of parameters: expected {len(function.params)}, got {len(params)}"
        )
    for i, param in enumerate(function.params):
        new_frame[param] = evaluate(params[i], frame)
    return evaluate(function.body, new_frame)


def result_and_frame(tree, frame=None):
    if frame is None:
        frame = Frame(built_in_frame)
    return evaluate(tree, frame), frame


def repl(verbose=False):
    """
    Read in a single line of user input, evaluate the expression, and print
    out the result. Repeat until user inputs "QUIT"

    Arguments:
        verbose: optional argument, if True will display tokens and parsed
            expression in addition to more detailed error output.
    """
    import traceback

    _, frame = result_and_frame(["+"])  # make a global frame
    while True:
        input_str = input("in> ")
        if input_str == "QUIT":
            return
        try:
            token_list = tokenize(input_str)
            if verbose:
                print("tokens>", token_list)
            expression = parse(token_list)
            if verbose:
                print("expression>", expression)
            output, frame = result_and_frame(expression, frame)
            print("  out>", output)
        except SchemeError as e:
            if verbose:
                traceback.print_tb(e.__traceback__)
            print("Error>", repr(e))


if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()
    repl(True)
