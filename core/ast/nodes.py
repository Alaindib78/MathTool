class ASTNode:
    pass

class ProgramNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"ProgramNode({self.statements})"
    
class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"NumberNode({self.value})"


class IdentifierNode(ASTNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"IdentifierNode({self.name})"


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
            f"{self.right})"
        )


class UnaryOpNode(ASTNode):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

    def __repr__(self):
        return (
            f"UnaryOpNode("
            f"{self.operator}, "
            f"{self.operand})"
        )


class AssignmentNode(ASTNode):
    def __init__(self, target, value):
        self.target = target
        self.value = value

    def __repr__(self):
        return (
            f"AssignmentNode("
            f"{self.target}, "
            f"{self.value})"
        )
    
class IfNode(ASTNode):
    def __init__(
        self,
        condition,
        then_branch,
        elseif_branches,
        else_branch
    ):
        self.condition = condition
        self.then_branch = then_branch
        self.elseif_branches = elseif_branches
        self.else_branch = else_branch

    def __repr__(self):
        return (
            f"IfNode("
            f"condition={self.condition}, "
            f"then={self.then_branch}, "
            f"elseif={self.elseif_branches}, "
            f"else={self.else_branch}"
            f")"
        )
