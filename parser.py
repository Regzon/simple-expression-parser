#!/usr/bin/env python3


class LexicalError(Exception):
    def __init__(self, msg="Lexical error", **kwargs):
        super().__init__(msg, **kwargs)


class Lexer:
    ALLOWED_SYMBOLS = ('<', '>', '=', '+', '-', '*', '(', ')')

    def __init__(self, source):
        self.source = source
        self.index = 0

    def is_digit(self):
        return self.source[self.index].isdigit()

    def is_symbol(self):
        return self.source[self.index] in self.ALLOWED_SYMBOLS

    def next_token(self):
        while self.index < len(self.source):
            if self.is_digit():
                return self.next_number()
            elif self.is_symbol():
                return self.next_symbol()
            elif self.source[self.index] == ' ':
                self.index += 1
                continue
            else:
                symbol = self.source[self.index]
                raise LexicalError(f"Invalid symbol: {symbol}")
        return None

    def next_number(self):
        number = ''
        while self.index < len(self.source) and self.is_digit():
            number += self.source[self.index]
            self.index += 1
        return number

    def next_symbol(self):
        token = self.source[self.index]
        self.index += 1
        return token


class SyntaxError(Exception):
    def __init__(self, msg="Syntax error", **kwargs):
        super().__init__(msg, **kwargs)


class Expression:
    pass


class Primary(Expression):
    pass


class Integer(Primary):
    def __init__(self, number):
        self.number = number
        assert self.number.isdigit()

    def calculate(self):
        return int(self.number)

    def __str__(self):
        return f'Integer({self.number})'


class Parenthesized(Primary):
    def __init__(self, expression):
        self.expression = expression
        assert isinstance(self.expression, Expression)

    def calculate(self):
        return self.expression.calculate()

    def __str__(self):
        return f'Parenthesized({self.expression})'


class Binary(Expression):
    def __init__(self, left, right):
        self.left = left
        self.right = right


class Relation(Binary):
    def __init__(self, left, right):
        assert isinstance(left, Term)
        assert right is None or isinstance(right, Term)
        super().__init__(left, right)


class Less(Relation):
    def calculate(self):
        return 1 if self.left.calculate() < self.right.calculate() else 0

    def __str__(self):
        return f'Less({self.left},{self.right})'


class Greater(Relation):
    def calculate(self):
        return 1 if self.left.calculate() > self.right.calculate() else 0

    def __str__(self):
        return f'Greater({self.left},{self.right})'


class Equal(Relation):
    def calculate(self):
        return 1 if self.left.calculate() == self.right.calculate() else 0

    def __str__(self):
        return f'Equal({self.left},{self.right})'


class SingleRelation(Relation):
    def __init__(self, term):
        assert isinstance(term, Term)
        super().__init__(left=term, right=None)

    def calculate(self):
        return self.left.calculate()

    def __str__(self):
        return f'SingleRelation({self.left})'


class Term(Binary):
    def __init__(self, left, right):
        assert isinstance(left, Term) or isinstance(left, Factor)
        assert right is None or isinstance(right, Factor)
        super().__init__(left, right)


class AddTerm(Term):
    def calculate(self):
        return self.left.calculate() + self.right.calculate()

    def __str__(self):
        return f'AddTerm({self.left},{self.right})'


class SubTerm(Term):
    def calculate(self):
        return self.left.calculate() - self.right.calculate()

    def __str__(self):
        return f'SubTerm({self.left},{self.right})'


class SingleTerm(Term):
    def __init__(self, factor):
        assert isinstance(factor, Factor)
        super().__init__(left=factor, right=None)

    def calculate(self):
        return self.left.calculate()

    def __str__(self):
        return f'SingleTerm({self.left})'


class Factor(Binary):
    def __init__(self, left, right):
        assert isinstance(left, Factor) or isinstance(left, Primary)
        assert right is None or isinstance(right, Primary)
        super().__init__(left, right)

    def calculate(self):
        return self.left.calculate() * self.right.calculate()

    def __str__(self):
        return f'Factor({self.left},{self.right})'


class SingleFactor(Factor):
    def __init__(self, primary):
        assert isinstance(primary, Primary)
        super().__init__(left=primary, right=None)

    def calculate(self):
        return self.left.calculate()

    def __str__(self):
        return f'SingleFactor({self.left})'


class Parser:
    def __init__(self, expression_string):
        self.expression_string = expression_string
        self.lexer = Lexer(self.expression_string)
        self.token = None

    def current_token(self):
        return self.token

    def next_token(self):
        self.token = self.lexer.next_token()
        return self.token

    def parse(self):
        return self.parse_relation()

    def parse_relation(self):
        left = self.parse_term()

        token = self.current_token()
        if token == '<':
            right = self.parse_term()
            return Less(left, right)
        elif token == '>':
            right = self.parse_term()
            return Greater(left, right)
        elif token == '=':
            right = self.parse_term()
            return Equal(left, right)

        return SingleRelation(left)

    def parse_term(self):
        left = self.parse_factor()
        right = None

        token = self.current_token()
        while token in ('+', '-'):
            right = self.parse_factor()
            if token == '+':
                left = AddTerm(left, right)
            elif token == '-':
                left = SubTerm(left, right)
            token = self.current_token()

        if right is None:
            left = SingleTerm(left)

        return left

    def parse_factor(self):
        left = self.parse_primary()
        right = None

        token = self.next_token()
        while token == '*':
            right = self.parse_primary()
            left = Factor(left, right)
            token = self.next_token()

        if right is None:
            left = SingleFactor(left)

        return left

    def parse_primary(self):
        token = self.next_token()
        if token.isdigit():
            primary = Integer(token)
        elif token == '(':
            expression = self.parse()
            token = self.current_token()
            if token != ')':
                raise SyntaxError(f"Expected ')', got '{token}'")
            primary = Parenthesized(expression)
        else:
            raise SyntaxError(
                f"Expected integer or parenthesis, got '{token}'"
            )
        return primary


def main():
    expression_string = input("Enter the expression: ")
    parser = Parser(expression_string)
    expression_tree = parser.parse()
    print("Expression:", expression_tree)
    result = expression_tree.calculate()
    print("Result:", result)


if __name__ == '__main__':
    main()
