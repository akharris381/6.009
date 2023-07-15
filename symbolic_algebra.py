"""
6.1010 Spring '23 Lab 10: Symbolic Algebra
"""

import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Symbol:
    """
    Encompasses all symbolic expressions:
    numbers, variables, and operations
    """

    precedence = 0
    right_parens = False
    left_parens = False

    def __add__(self, other_item):
        return Add(self, other_item)

    def __radd__(self, other_item):
        return Add(other_item, self)

    def __sub__(self, other_item):
        return Sub(self, other_item)

    def __rsub__(self, other_item):
        return Sub(other_item, self)

    def __mul__(self, other_item):
        return Mul(self, other_item)

    def __rmul__(self, other_item):
        return Mul(other_item, self)

    def __truediv__(self, other_item):
        return Div(self, other_item)

    def __rtruediv__(self, other_item):
        return Div(other_item, self)

    def __pow__(self, other_item):
        return Pow(self, other_item)

    def __rpow__(self, other_item):
        return Pow(other_item, self)

    def simplify(self):
        return self


class Var(Symbol):
    """
    Variables, subclass of Symbol
    """

    precedence = 4

    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Var('{self.name}')"

    def eval(self, mapping):
        if self.name in mapping:
            return mapping[self.name]
        else:
            raise NameError(f"{self.name} not in mapping")

    def __eq__(self, other_symbol):
        return isinstance(other_symbol, Var) and self.name == other_symbol.name

    def deriv(self, other_name):
        return Num(1) if self.name == other_name else Num(0)


class Num(Symbol):
    """
    Number, subclass of Symbol
    """

    precedence = 4

    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return f"Num({self.n})"

    def eval(self, mapping):
        return self.n

    def __eq__(self, other_symbol):
        return isinstance(other_symbol, Num) and self.n == other_symbol.n

    def deriv(self, other_name):
        return Num(0)


class BinOp(Symbol):
    """
    Binary operations +, -, *, /, subclass of Symbol.
    """

    def __init__(self, left, right):
        if isinstance(left, str):
            self.left = Var(left)
        elif isinstance(left, (int, float)):
            self.left = Num(left)
        else:
            self.left = left
        if isinstance(right, str):
            self.right = Var(right)
        elif isinstance(right, (int, float)):
            self.right = Num(right)
        else:
            self.right = right

    def __str__(self):
        if (0 < self.left.precedence < self.precedence) or (
            self.left_parens and self.left.precedence <= self.precedence
        ):
            left_string = f"({str(self.left)})"
        else:
            left_string = str(self.left)
        if 0 < self.right.precedence < self.precedence or (
            self.right_parens and self.precedence == self.right.precedence
        ):
            right_string = f"({str(self.right)})"
        else:
            right_string = str(self.right)
        return f"{left_string} {self.operation} {right_string}"

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.left)}, {repr(self.right)})"

    def eval(self, mapping):
        """
        Evaluates a symbolic expression given the values assigned by mapping.
        """
        if self.operation == "+":
            return self.left.eval(mapping) + self.right.eval(mapping)
        elif self.operation == "-":
            return self.left.eval(mapping) - self.right.eval(mapping)
        elif self.operation == "*":
            return self.left.eval(mapping) * self.right.eval(mapping)
        elif self.operation == "/":
            return self.left.eval(mapping) / self.right.eval(mapping)
        elif self.operation == "**":
            return self.left.eval(mapping) ** self.right.eval(mapping)

    def __eq__(self, other_symbol):
        return (
            isinstance(other_symbol, BinOp)
            and self.left == other_symbol.left
            and self.right == other_symbol.right
            and self.operation == other_symbol.operation
        )


class Add(BinOp):
    """
    Addition, subclass of BinOp
    """

    operation = "+"
    precedence = 1

    def deriv(self, other_name):
        return self.left.deriv(other_name) + self.right.deriv(other_name)

    def simplify(self):
        left_simple = self.left.simplify()
        right_simple = self.right.simplify()
        if left_simple == Num(0):
            return right_simple
        elif right_simple == Num(0):
            return left_simple
        elif hasattr(left_simple, "n") and hasattr(right_simple, "n"):
            return Num(left_simple.n + right_simple.n)
        else:
            return left_simple + right_simple


class Sub(BinOp):
    """
    Subtraction, subclass of BinOp
    """

    operation = "-"
    precedence = 1
    right_parens = True

    def deriv(self, other_name):
        return self.left.deriv(other_name) - self.right.deriv(other_name)

    def simplify(self):
        left_simple = self.left.simplify()
        right_simple = self.right.simplify()
        if right_simple == Num(0):
            return left_simple
        elif hasattr(left_simple, "n") and hasattr(right_simple, "n"):
            return Num(left_simple.n - right_simple.n)
        else:
            return left_simple - right_simple


class Mul(BinOp):
    """
    Multiplication, subclass of BinOp
    """

    operation = "*"
    precedence = 2

    def deriv(self, other_name):
        return self.left * self.right.deriv(other_name) + self.right * self.left.deriv(
            other_name
        )

    def simplify(self):
        left_simple = self.left.simplify()
        right_simple = self.right.simplify()
        if left_simple == Num(0) or right_simple == Num(0):
            return Num(0)
        elif left_simple == Num(1):
            return right_simple
        elif right_simple == Num(1):
            return left_simple
        elif hasattr(left_simple, "n") and hasattr(right_simple, "n"):
            return Num(left_simple.n * right_simple.n)
        else:
            return left_simple * right_simple


class Div(BinOp):
    """
    Division, subclass of BinOp
    """

    operation = "/"
    precedence = 2
    right_parens = True

    def deriv(self, other_name):
        return (
            self.right * self.left.deriv(other_name)
            - self.left * self.right.deriv(other_name)
        ) / (self.right * self.right)

    def simplify(self):
        left_simple = self.left.simplify()
        right_simple = self.right.simplify()
        if left_simple == Num(0):
            return Num(0)
        elif right_simple == Num(1):
            return left_simple
        elif hasattr(left_simple, "n") and hasattr(right_simple, "n"):
            return Num(left_simple.n / right_simple.n)
        else:
            return left_simple / right_simple


class Pow(BinOp):
    """
    Exponentiation, subclass of BinOp
    """

    operation = "**"
    precedence = 3
    left_parens = True

    def deriv(self, other_name):
        if hasattr(self.right, "n"):
            return (
                self.right * self.left ** (self.right - 1) * self.left.deriv(other_name)
            )
        else:
            raise TypeError("self.right is not a number")

    def simplify(self):
        left_simple = self.left.simplify()
        right_simple = self.right.simplify()
        if right_simple == Num(0):
            return Num(1)
        elif right_simple == Num(1):
            return left_simple
        elif left_simple == Num(0) and not (
            hasattr(right_simple, "n") and right_simple.n < 0
        ):
            return Num(0)
        elif hasattr(left_simple, "n") and hasattr(right_simple, "n"):
            return Num(left_simple.n**right_simple.n)
        else:
            return left_simple**right_simple


def expression(string_input):
    """
    Converts string into symbolic expression
    """

    def tokenize(string_input):
        tokens = []
        i = 0
        while i < len(string_input):
            char = string_input[i]
            if char in {" ", ")"}:
                pass
            elif char == "*":
                if i + 1 < len(string_input) and string_input[i + 1] == "*":
                    tokens.append("**")
                    i += 1
                else:
                    tokens.append("*")
            elif char in {"(", "/", "+"} or char in "abcdefghijklmnopqrstuvwxyz":
                tokens.append(char)
            else:
                start = int(i)
                while (
                    i < len(string_input) - 1
                    and string_input[i + 1] not in {"(", ")", "*", "/", "+", " "}
                    and string_input[i + 1] not in "abcdefghijklmnopqrstuvwxyz"
                ):
                    i += 1
                tokens.append(string_input[start : i + 1])
            i += 1
        return tokens

    def parse(tokens):
        def parse_expression(index):
            char = tokens[index]
            try:
                return Num(float(char)), index + 1
            except ValueError:
                pass
            if char != "(":
                return Var(char), index + 1
            else:
                left_exp, op_loc = parse_expression(index + 1)
                right_exp, next_index = parse_expression(op_loc + 1)
                if tokens[op_loc] == "+":
                    return Add(left_exp, right_exp), next_index
                elif tokens[op_loc] == "-":
                    return Sub(left_exp, right_exp), next_index
                elif tokens[op_loc] == "*":
                    return Mul(left_exp, right_exp), next_index
                elif tokens[op_loc] == "/":
                    return Div(left_exp, right_exp), next_index
                elif tokens[op_loc] == "**":
                    return Pow(left_exp, right_exp), next_index

        return parse_expression(0)[0]

    return parse(tokenize(string_input))


if __name__ == "__main__":
    doctest.testmod()
