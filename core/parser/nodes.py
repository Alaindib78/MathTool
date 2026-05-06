class ASTNode:
    pass

class NumberNode(ASTNode):

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"NumberNode({self.value})"
    
class VariableNode(ASTNode):

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"VariableNode({self.name})"
    
class BinaryOpNode(ASTNode):

    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):

        return (
            f"BinaryOpNode("
            f"{self.left}, "
            f"{self.operator}, "
            f"{self.right}"
            f")"
        )
    
class AssignmentNode(ASTNode):

    def __init__(self, variable, value):
        self.variable = variable
        self.value = value

    def __repr__(self):

        return (
            f"AssignmentNode("
            f"{self.variable}, "
            f"{self.value}"
            f")"
        )
    
class CompoundNode(ASTNode):

    def __init__(self):
        self.statements = []

    def add(self, statement):
        self.statements.append(statement)

    def __repr__(self):
        return f"CompoundNode({self.statements})"
    
