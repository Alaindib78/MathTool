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


class SymbolicEquation:
    def __init__(self, left, right):
        self.left = str(left)
        self.right = str(right)

    @property
    def expression(self):
        return f"{self.left} == {self.right}"

    def __str__(self):
        return self.expression

    def __repr__(self):
        return self.expression

    def __eq__(self, other):
        if not isinstance(other, SymbolicEquation):
            return False

        return (
            self.left == other.left
            and self.right == other.right
        )


class NameValueOption:
    def __init__(self, name, value):
        self.name = str(name)
        self.value = value
