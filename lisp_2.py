"""
6.1010 Spring '23 Lab 12: LISP Interpreter Part 2
"""
#!/usr/bin/env python3
import sys

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


def compare(args, func):
    if len(args) == 1:
        return True
    return compare(args[1:], func) and func(args[0], args[1])


def eq(args):
    return compare(args, lambda x, y: x == y)


def greater(args):
    return compare(args, lambda x, y: x > y)


def greater_or_eq(args):
    return compare(args, lambda x, y: x >= y)


def less(args):
    return compare(args, lambda x, y: x < y)


def less_or_eq(args):
    return compare(args, lambda x, y: x <= y)


def cons(args):
    return Pair(args[0], args[1])


def car(args):
    if isinstance(args[0], Pair):
        return args[0].car
    raise SchemeEvaluationError(f"{args[0]} is not a pair")


def cdr(args):
    if isinstance(args[0], Pair):
        return args[0].cdr
    raise SchemeEvaluationError(f"{args[0]} is not a pair")


def make_list(args):
    if args:
        return Pair(args[0], make_list(args[1:]))
    return None


def is_list(args):
    if isinstance(args, list):
        arg = args[0]
    else:
        arg = args
    if arg is None:
        return True
    return isinstance(arg, Pair) and is_list(arg.cdr)


def length(args):
    if isinstance(args, list):
        arg = args[0]
    else:
        arg = args
    if not is_list(arg):
        raise SchemeEvaluationError("not a list")
    if not arg:
        return 0
    return 1 + length(arg.cdr)


def value_at_index(args):
    index = args[1]
    if isinstance(args[0], list):
        arg = args[0][0]
    elif isinstance(args, list):
        arg = args[0]
    # else:
    #     arg = args
    if not isinstance(arg, Pair):
        raise SchemeEvaluationError("not a list")
    elif arg is None:
        raise SchemeEvaluationError("index out of range")
    elif arg.cdr is None:
        if index != 0:
            raise SchemeEvaluationError("index out of range")
        return arg.car
    elif index == 0:
        if arg is None:
            raise SchemeEvaluationError("index out of range")
        return arg.car
    return value_at_index([arg.cdr, index - 1])


def append(args):
    if not args:
        return None
    elif not is_list(args[0]):
        raise SchemeEvaluationError("not a list")
    elif len(args) == 1:
        return args[0]
    elif args[0] is None:
        return append(args[1:])
    return Pair(args[0].car, append([args[0].cdr] + args[1:]))


def map(args):
    if not isinstance(args, list):
        raise SchemeEvaluationError("args is not a list")
    func = args[0]
    init_list = args[1]
    if init_list is None:
        return None
    elif not isinstance(init_list, Pair):
        raise SchemeEvaluationError("not a list")
    if func in scheme_builtins.values():
        return Pair(func(init_list.car), map([func, init_list.cdr]))
    elif isinstance(func, Function):
        new_frame = Frame(func.frame)
        new_frame[func.params[0]] = init_list.car
        return Pair(evaluate(func.body, new_frame), map([func, init_list.cdr]))


def filter(args):
    if not isinstance(args, list):
        raise SchemeEvaluationError("args is not a list")
    func = args[0]
    init_list = args[1]
    if init_list is None:
        return None
    elif not isinstance(init_list, Pair):
        raise SchemeEvaluationError("not a list")
    if func in scheme_builtins.values():
        if func(init_list.car):
            return Pair(init_list.car, filter([func, init_list.cdr]))
        return filter([func, init_list.cdr])
    elif isinstance(func, Function):
        new_frame = Frame(func.frame)
        new_frame[func.params[0]] = init_list.car
        if evaluate(func.body, new_frame):
            return Pair(init_list.car, filter([func, init_list.cdr]))
        return filter([func, init_list.cdr])


def reduce(args):
    if not isinstance(args, list):
        raise SchemeEvaluationError("args is not a list")
    func = args[0]
    init_list = args[1]
    init_val = args[2]
    if init_list is None:
        return init_val
    elif not isinstance(init_list, Pair):
        raise SchemeEvaluationError("not a list")
    if func in scheme_builtins.values():
        return reduce([func, init_list.cdr, func([init_val, init_list.car])])
    elif isinstance(func, Function):
        new_frame = Frame(func.frame)
        new_frame[func.params[0]] = init_val
        new_frame[func.params[1]] = init_list.car
        return reduce([func, init_list.cdr, evaluate(func.body, new_frame)])


scheme_builtins = {
    "+": sum,
    "-": lambda args: -args
    if isinstance(args, (float, int))
    else -args[0]
    if len(args) == 1
    else (args[0] - sum(args[1:])),
    "*": product,
    "/": quotient,
    "equal?": eq,
    ">": greater,
    ">=": greater_or_eq,
    "<": less,
    "<=": less_or_eq,
    "not": lambda args: not args[0],
    "#t": True,
    "#f": False,
    "cons": cons,
    "car": car,
    "cdr": cdr,
    "nil": None,
    "list": make_list,
    "list?": is_list,
    "length": length,
    "list-ref": value_at_index,
    "append": append,
    "map": map,
    "filter": filter,
    "reduce": reduce,
    "begin": lambda args: args[-1],
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

    def delete(self, var):
        try:
            return self.bindings.pop(var)
        except:
            raise SchemeNameError("var not bound locally")


built_in_frame = Frame()
built_in_frame.bindings = scheme_builtins


class Function:
    def __init__(self, body, params, frame):
        self.body = body
        self.params = params
        self.frame = frame


class Pair:
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr


special_forms = {"lambda", "define", "if", "and", "or", "del", "let"}


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
    if tree == []:
        raise SchemeEvaluationError("empty tree")
    if frame is None:
        frame = Frame(built_in_frame)
    if isinstance(tree, str):
        return evaluate_string(tree, frame)
    elif isinstance(tree, (int, float)):
        return tree
    else:
        first = evaluate(tree[0], frame)
        print(first)
        if first in {"lambda", "define"}:
            var = tree[1]
            val = tree[2]
            if first == "define":
                return define(frame, var, val)
            if first == "lambda":
                return Function(val, var, frame)
        elif first == "if":
            if evaluate(tree[1], frame):
                return evaluate(tree[2], frame)
            return evaluate(tree[3], frame)
        elif first == "and":
            return evaluate_and(tree, frame)
        elif first == "or":
            return evaluate_or(tree, frame)
        elif first == "del":
            return frame.delete(tree[1])
        elif first == "let":
            new_frame = Frame(frame)
            for binding in tree[1]:
                new_frame.bindings[binding[0]] = evaluate(binding[1], frame)
            return evaluate(tree[2], new_frame)
        elif isinstance(first, Function):
            return evaluate_function(first, tree, frame)
        elif (
            not isinstance(tree[0], list)
            and tree[0] in {"not", "car", "cdr", "list?", "length"}
            and len(tree[1:]) != 1
        ):
            raise SchemeEvaluationError(f"wrong number of args for {tree[0]}")
        elif (
            not isinstance(tree[0], list)
            and tree[0] in {"cons", "list-ref", "map", "filter"}
            and len(tree[1:]) != 2
        ):
            raise SchemeEvaluationError(f"wrong number of args for {tree[0]}")
        elif (
            not isinstance(tree[0], list) and tree[0] == "reduce" and len(tree[1:]) != 3
        ):
            raise SchemeEvaluationError(f"wrong number of args for reduce")
        elif first in scheme_builtins.values() and not isinstance(
            first, (float, str, int)
        ):
            return first([evaluate(item, frame) for item in tree[1:]])
        raise SchemeEvaluationError(f"{first} is not a valid function")


def evaluate_string(tree, frame):
    if isinstance(tree, str):
        if tree in special_forms:
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


def evaluate_and(tree, frame):
    for sub_exp in tree[1:]:
        if not evaluate(sub_exp, frame):
            return False
    return True


def evaluate_or(tree, frame):
    for sub_exp in tree[1:]:
        if evaluate(sub_exp, frame):
            return True
    return False


def result_and_frame(tree, frame=None):
    if frame is None:
        frame = Frame(built_in_frame)
    return evaluate(tree, frame), frame


def evaluate_file(filename, frame=None):
    with open(filename, "r") as f:
        source = "".join(f.readlines())
        tokens = tokenize(source)
        expression = parse(tokens)
        return evaluate(expression, frame)


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
