from core.lexer.token import TokenType

from core.parser.nodes import (
    NumberNode,
    VariableNode,
    BinaryOpNode,
    AssignmentNode,
    CompoundNode
)

from core.runtime.context import Context

class Interpreter:

    def __init__(self):

        self.context = Context()

    def visit(self, node):

        method_name = (
            f"visit_{type(node).__name__}"
        )

        method = getattr(
            self,
            method_name,
            self.no_visit_method
        )

        return method(node)
    
    def no_visit_method(self, node):

        raise Exception(
            f"No visit_{type(node).__name__} method defined"
        )
    
    def visit_NumberNode(self, node):

        return node.value
    
    def visit_VariableNode(self, node):

        return self.context.get_variable(node.name)
    
    def visit_BinaryOpNode(self, node):

        left = self.visit(node.left)
        right = self.visit(node.right)

        if node.operator == TokenType.PLUS:
            return left + right

        elif node.operator == TokenType.MINUS:
            return left - right

        elif node.operator == TokenType.MUL:
            return left * right

        elif node.operator == TokenType.DIV:

            if right == 0:
                raise Exception(
                    "Division by zero"
                )

            return left / right

        raise Exception(
            f"Unknown operator {node.operator}"
        )
    
    def visit_AssignmentNode(self, node):

        variable_name = node.variable.name

        value = self.visit(node.value)

        self.context.set_variable(
            variable_name,
            value
        )

        return value
    
    def visit_CompoundNode(self, node):

        results = []

        for statement in node.statements:

            result = self.visit(statement)

            results.append(result)

        return results
    
    def interpret(self, tree):

        return self.visit(tree)

"""    
if __name__ == "__main__":

    from core.lexer.lexer import Lexer
    from core.parser.parser import Parser

    source = "
    A = 2 + 3 * 4;
    B = A + 10;
    "

    lexer = Lexer(source)

    tokens = lexer.tokenize()

    parser = Parser(tokens)

    tree = parser.parse()

    interpreter = Interpreter()

    result = interpreter.interpret(tree)

    print("Execution Results:")
    print(result)

    print("\nVariables:")
    print(interpreter.context)
"""