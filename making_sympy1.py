from abc import ABC, abstractmethod
from typing import Union
import re


class Expression(ABC):
    @abstractmethod
    def derivative(self) -> "Expression":
        pass

    def __add__(self, other):
        if isinstance(other, (int, float)):
            other = Constant(other)
        return Addition(self, other)

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            other = Constant(other)
        return Multiplication(self, other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            other = Constant(other)
        return Division(self, other)

    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            other = Constant(other)
        return Division(Constant(other), self)


class Variable(Expression):
    def __init__(self, name: str):
        self.name = name

    def derivative(self) -> "Expression":
        return Constant(1)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def __pow__(self, other):
        if isinstance(other, (int, float)):
            other = Constant(other)
        return Power(self, other)


class Constant(Expression):
    def __init__(self, value: float):
        self.value = value

    def derivative(self) -> "Expression":
        return Constant(0)

    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return str(self.value)


class Addition(Expression):
    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right

    def derivative(self) -> Expression:
        return self.left.derivative() + self.right.derivative()

    def __repr__(self):
        return f"({self.left} + {self.right})"


class Multiplication(Expression):
    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right

    def derivative(self) -> Expression:
        return Addition(
            Multiplication(self.left.derivative(), self.right),
            Multiplication(self.left, self.right.derivative()),
        )

    def __repr__(self):
        return f"({self.left} * {self.right})"


class Division(Expression):
    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right

    def derivative(self) -> Expression:
        numerator = Subtraction(
            Multiplication(self.left.derivative(), self.right),
            Multiplication(self.left, self.right.derivative()),
        )
        denominator = Multiplication(self.right, self.right)
        return Division(numerator, denominator)

    def __repr__(self):
        return f"({self.left} / {self.right})"


class Subtraction(Expression):
    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right

    def derivative(self) -> Expression:
        return self.left.derivative() - self.right.derivative()

    def __repr__(self):
        return f"({self.left} - {self.right})"


class Power(Expression):
    def __init__(self, base: Expression, exponent: Expression):
        self.base = base
        self.exponent = exponent

    def derivative(self) -> Expression:
        if isinstance(self.exponent, Constant):
            new_exponent = Constant(self.exponent.value - 1)
            return Multiplication(
                Multiplication(self.exponent, Power(self.base, new_exponent)), self.base.derivative()
            )
        else:
            raise NotImplementedError("Non-constant exponents are not supported")

    def __repr__(self):
        return f"({self.base} ** {self.exponent})"


def input_expression() -> Expression:
    print("Enter a function in terms of x using operators +, *, /, **")
    print("Example: 1/x or x**2 + 2*x + 1")
    expr_str = input("> ")

    x = Variable("x")
    env = {
        "x": x,
        "Constant": Constant,
        "Variable": Variable,
        "Addition": Addition,
        "Subtraction": Subtraction,
        "Multiplication": Multiplication,
        "Division": Division,
        "Power": Power,
        "__builtins__": None,
    }

    # Convert numeric literals to Constant objects
    def replace_numbers(match):
        return f"Constant({match.group()})"

    expr_str = re.sub(r"\b\d+\b", replace_numbers, expr_str)

    # Handle 1/x case by converting 1/x to x**-1
    expr_str = re.sub(r"1\s*/\s*x", r"x**-1", expr_str)

    # Ensure all exponents are correctly parsed to use `Power` class
    expr_str = re.sub(r"(x)\s*\*\*\s*(\d+)", r"Power(\1, Constant(\2))", expr_str)

    try:
        print(f"Evaluating expression: {expr_str}")
        expr = eval(expr_str, env)
        return expr
    except Exception as e:
        print(f"Error: {e}")
        return None


def output_derivative():
    expr = input_expression()
    if expr:
        print(f"\nf(x) = {expr}")
        derivative = expr.derivative()
        print(f"f'(x) = {derivative}\n")


if __name__ == "__main__":
    print("Formal Differentiation Calculator")
    print("Enter 'q' to quit")
    while True:
        print("\nEnter a function to differentiate:")
        output_derivative()
        if input("\nContinue? (y/q): ").lower() != "y":
            break
