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


class StringNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'StringNode("{self.value}")'

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
    
class WhileNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return (
            f"WhileNode("
            f"condition={self.condition}, "
            f"body={self.body})"
        )


class RangeNode(ASTNode):
    def __init__(self, start, step, end):
        self.start = start
        self.step = step
        self.end = end

    def __repr__(self):
        return (
            f"RangeNode("
            f"start={self.start}, "
            f"step={self.step}, "
            f"end={self.end})"
        )
    
class MatrixNode(ASTNode):
    def __init__(self, rows):
        self.rows = rows

    def __repr__(self):
        return f"MatrixNode(rows={self.rows})"


class ForNode(ASTNode):
    def __init__(self, variable, iterable, body):
        self.variable = variable
        self.iterable = iterable
        self.body = body

    def __repr__(self):
        return (
            f"ForNode("
            f"variable={self.variable}, "
            f"iterable={self.iterable}, "
            f"body={self.body})"
        )
    
class FunctionCallNode(ASTNode):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def __repr__(self):
        return (
            f"FunctionCallNode("
            f"name={self.name}, "
            f"arguments={self.arguments})"
        )

class FunctionDeclarationNode(ASTNode):
    def __init__(
        self,
        name,
        parameters,
        body,
        return_variable
    ):
        self.name = name
        self.parameters = parameters
        self.body = body
        self.return_variable = return_variable

    def __repr__(self):
        return (
            f"FunctionDeclarationNode("
            f"name={self.name}, "
            f"parameters={self.parameters})"
        )


class ReturnNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"ReturnNode({self.value})"
    
"""    
class IndexNode(ASTNode):
    def __init__(self, target, indices):
        self.target = target
        self.indices = indices

    def __repr__(self):
        return (
            f"IndexNode("
            f"target={self.target}, "
            f"indices={self.indices})"
        )
"""