from core.ast.nodes import (
    ProgramNode,
    NumberNode,
    IdentifierNode,
    BinaryOpNode,
    UnaryOpNode,
    AssignmentNode,
)

from core.lexer.token import TokenType


class Interpreter:
    def __init__(self, context):
        self.context = context

    def evaluate(self, node):
        method_name = f"visit_{type(node).__name__}"

        method = getattr(
            self,
            method_name,
            self.no_visit_method
        )

        return method(node)

    def no_visit_method(self, node):
        raise Exception(
            f"No visit method for {type(node).__name__}"
        )

    # -------------------------
    # Node Visitors
    # -------------------------
    
    def visit_ProgramNode(self, node):
        result = None

        for statement in node.statements:
            result = self.evaluate(statement)

        return result

    def visit_NumberNode(self, node):
        return node.value

    def visit_IdentifierNode(self, node):
        return self.context.get_variable(node.name)

    def visit_AssignmentNode(self, node):
        value = self.evaluate(node.value)

        self.context.set_variable(
            node.target.name,
            value
        )

        return value

    def visit_UnaryOpNode(self, node):
        value = self.evaluate(node.operand)

        if node.operator == TokenType.MINUS:
            return -value

        if node.operator == TokenType.PLUS:
            return +value

        raise Exception(
            f"Unsupported unary operator "
            f"{node.operator}"
        )

    def visit_BinaryOpNode(self, node):
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)

        operator = node.operator

        if operator == TokenType.PLUS:
            return left + right

        if operator == TokenType.MINUS:
            return left - right

        if operator == TokenType.STAR:
            return left * right

        if operator == TokenType.SLASH:
            if right == 0:
                raise Exception("Division by zero")

            return left / right

        if operator == TokenType.MODULO:
            return left % right

        if operator == TokenType.CARET:
            return left ** right

        raise Exception(
            f"Unsupported operator {operator}"
        )