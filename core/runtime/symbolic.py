class SymbolicValue:
    def __init__(self, expression):
        self.expression = str(expression)

    def __str__(self):
        return self.expression

    def __repr__(self):
        return self.expression

    def __eq__(self, other):
        if not isinstance(other, SymbolicValue):
            return False

        return self.expression == other.expression
