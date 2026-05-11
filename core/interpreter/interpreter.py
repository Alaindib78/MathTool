from ast import arg, operator
from platform import node
from turtle import right
import numpy as np

from core.ast.nodes import (
    ProgramNode,
    NumberNode,
    StringNode,
    IdentifierNode,
    BinaryOpNode,
    UnaryOpNode,
    AssignmentNode,
    IfNode,
    WhileNode,
    RangeNode,
    MatrixNode,
    ForNode,
    FunctionCallNode,
    FunctionDeclarationNode,
    ReturnNode,
)
from core.lexer.token import TokenType
from core.runtime.user_function import UserFunction
from core.interpreter.return_exception import ReturnException
from core.errors.errors import RuntimeError
from core.runtime.call_stack import CallFrame

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
        raise RuntimeError(
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
    
    def visit_StringNode(self, node):
        return node.value

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
        
        if node.operator == TokenType.NOT:
            return not value

        raise RuntimeError(
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

#        if operator == TokenType.STAR:
#            return left * right
        if operator == TokenType.STAR:
            if (
                isinstance(left, np.ndarray)
                and isinstance(right, np.ndarray)
            ):
                return left @ right

            return left * right
        
        if operator == TokenType.SLASH:
            if right == 0:
                raise RuntimeError(
                    "Division by zero"
                )

            return left / right
        
        if operator == TokenType.DOTSTAR:
            return left * right

        if operator == TokenType.DOTSLASH:
            return left / right

        if operator == TokenType.DOTCARET:
            return left ** right

        if operator == TokenType.MODULO:
            return left % right

        if operator == TokenType.CARET:
            return left ** right
        
        if operator == TokenType.EQEQ:
            return left == right

        if operator == TokenType.NEQ:
            return left != right

        if operator == TokenType.LT:
            return left < right

        if operator == TokenType.GT:
            return left > right

        if operator == TokenType.LTE:
            return left <= right

        if operator == TokenType.GTE:
            return left >= right

        if operator == TokenType.AND:
            return left and right

        if operator == TokenType.OR:
            return left or right

        raise RuntimeError(
            f"Unsupported operator {operator}"
        )
    
    def visit_IfNode(self, node):
        if self.evaluate(node.condition):
            result = None

            for stmt in node.then_branch:
                result = self.evaluate(stmt)

            return result

        for condition, body in node.elseif_branches:
            if self.evaluate(condition):
                result = None

                for stmt in body:
                    result = self.evaluate(stmt)

                return result

        if node.else_branch is not None:
            result = None

            for stmt in node.else_branch:
                result = self.evaluate(stmt)

            return result

        return None
    
    def visit_RangeNode(self, node):
        start = self.evaluate(node.start)
        step = self.evaluate(node.step)
        end = self.evaluate(node.end)

        values = []

        current = start

        if step == 0:
            raise Exception(
                "Range step cannot be zero"
            )

        if step > 0:
            while current <= end:
                values.append(current)
                current += step
        else:
            while current >= end:
                values.append(current)
                current += step

        return values
    
    def visit_MatrixNode(self, node):
        evaluated_rows = []

        for row in node.rows:
            evaluated_row = [
                self.evaluate(value)
                for value in row
            ]

            evaluated_rows.append(evaluated_row)

        # Row vector simplification
        if len(evaluated_rows) == 1:
            return np.array(evaluated_rows[0])

        return np.array(evaluated_rows)
    
    def visit_WhileNode(self, node):
        result = None

        while self.evaluate(node.condition):
            for stmt in node.body:
                result = self.evaluate(stmt)

        return result
    
    def visit_ForNode(self, node):
        iterable = self.evaluate(node.iterable)

        if not isinstance(iterable, list):
            raise Exception(
                "For loop iterable must be a list"
            )

        result = None

        for value in iterable:
            self.context.set_variable(
                node.variable.name,
                value
            )

            for stmt in node.body:
                result = self.evaluate(stmt)

        return result
    
#    def visit_FunctionCallNode(self, node):
#        function = self.context.functions.get(node.name)
#
#        arguments = [self.evaluate(arg) for arg in node.arguments]
#
#        return function(self.context, *arguments)

    def visit_FunctionCallNode(self, node):
        arguments = [
            self.evaluate(arg)
            for arg in node.arguments
        ]

        # Built-in/user function
        if self.context.functions.exists(node.name):
            function = self.context.functions.get(
                node.name
            )

            # Builtin Python function
            if callable(function):
                return function(
                    self.context,
                    *arguments
                )

            # User-defined function
            if isinstance(function, UserFunction):
                declaration = function.declaration

                if len(arguments) != len(
                    declaration.parameters
                ):
                    raise RuntimeError(
                        f"Function '{node.name}' "
                        f"expects "
                        f"{len(declaration.parameters)} "
                        f"arguments"
                    )

            local_context = (
                self.context.create_child_context()
            )

            for param, value in zip(
                declaration.parameters,
                arguments
            ):
                local_context.set_variable(
                    param,
                    value
                )

            local_interpreter = Interpreter(
                local_context
            )

            # -----------------------------
            # Push call frame
            # -----------------------------

            self.context.call_stack.push(
                CallFrame(node.name)
            )

            try:
                result = None

                for stmt in declaration.body:
                    result = local_interpreter.evaluate(
                        stmt
                    )

            except ReturnException as ret:
                return ret.value
            finally:
                # -------------------------
                # Always pop frame
                # -------------------------

                self.context.call_stack.pop()

            # Implicit return variable
            if declaration.return_variable:
                return local_context.get_variable(
                    declaration.return_variable
                )

            return result
        
        # Otherwise treat as indexing
        target = self.context.get_variable(
            node.name
        )

        indices = [
            int(arg) - 1
            for arg in arguments
        ]

        if len(indices) == 1:
            return target[indices[0]]

        return target[tuple(indices)]
    
    def visit_IndexNode(self, node):
        target = self.evaluate(node.target)

        indices = [
            int(self.evaluate(index)) - 1
            for index in node.indices
        ]

        if len(indices) == 1:
            return target[indices[0]]

        return target[tuple(indices)]
    
    def visit_FunctionDeclarationNode(self, node):
        function = UserFunction(
            node,
            self.context
        )

        self.context.functions.register(
            node.name,
            function
        )

        return None
    
    def visit_ReturnNode(self, node):
        value = self.evaluate(node.value)

        raise ReturnException(value)