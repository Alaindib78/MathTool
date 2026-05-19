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
    NameValueNode,
    FunctionDeclarationNode,
    ReturnNode,
    SymsNode,
    TransposeNode,
)
from core.lexer.token import TokenType
from core.runtime.user_function import UserFunction
from core.runtime.function_resolver import (
    build_user_functions,
    top_level_function_declarations,
)
from core.interpreter.return_exception import ReturnException
from core.errors.errors import RuntimeError
from core.runtime.call_stack import CallFrame
from core.runtime.symbolic import (
    NameValueOption,
    SymbolicEquation,
    SymbolicValue,
)

class Interpreter:
    def __init__(self, context):
        self.context = context

    def evaluate(self, node, source_path=None):
        previous_source_path = None

        if source_path is not None:
            previous_source_path = (
                self.context.current_source_path
            )

            self.context.current_source_path = source_path

        method_name = f"visit_{type(node).__name__}"

        method = getattr(
            self,
            method_name,
            self.no_visit_method
        )

        if (
            self.context.debugger
            and node is not None
        ):
            self.context.debugger.before_node(
                node
            )

        try:
            return method(node)
        finally:
            if source_path is not None:
                self.context.current_source_path = (
                    previous_source_path
                )

    def no_visit_method(self, node):
        raise RuntimeError(
            f"No visit method for {type(node).__name__}"
        )

    # -------------------------
    # Node Visitors
    # -------------------------
    
    def visit_ProgramNode(self, node):
        result = None

        file_functions = build_user_functions(
            self.context,
            top_level_function_declarations(node),
            self.context.current_source_path,
        )

        self.context.push_file_functions(
            file_functions
        )

        try:
            for name, function in file_functions.items():
                self.context.functions.register(
                    name,
                    function,
                )

            for statement in node.statements:
                result = self.evaluate(statement)

                if self.should_store_ans(
                    statement,
                    result
                ):
                    self.context.set_variable(
                        "ans",
                        result
                    )

            return result
        finally:
            self.context.pop_file_functions()
    
    def visit_StringNode(self, node):
        return node.value

    def visit_NumberNode(self, node):
        return node.value

    def visit_IdentifierNode(self, node):
        return self.context.get_variable(node.name)

    def visit_NameValueNode(self, node):
        return NameValueOption(
            node.name,
            self.evaluate(node.value)
        )

    def visit_AssignmentNode(self, node):
        value = self.evaluate(node.value)

        if isinstance(node.target, IdentifierNode):
            self.context.set_variable(
                node.target.name,
                value
            )

            return value

        if isinstance(node.target, FunctionCallNode):
            target = self.context.get_variable(
                node.target.name
            )

            indices = self.coerce_indices([
                self.evaluate(arg)
                for arg in node.target.arguments
            ])

            if not indices:
                raise RuntimeError(
                    "Indexed assignment requires at least one index",
                    node.line,
                    node.column
                )

            try:
                target[self.index_key(indices)] = value
            except (IndexError, TypeError, ValueError) as error:
                raise RuntimeError(
                    f"Invalid indexed assignment: {error}",
                    node.line,
                    node.column
                )

            return value

        raise RuntimeError(
            "Invalid assignment target",
            node.line,
            node.column
        )

    def visit_UnaryOpNode(self, node):
        value = self.evaluate(node.operand)

        if isinstance(value, SymbolicValue):
            return self.symbolic_unary_operation(
                node.operator,
                value
            )

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

        if self.has_symbolic_operand(
            left,
            right
        ):
            return self.symbolic_binary_operation(
                left,
                operator,
                right
            )

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
            return self.elementwise_multiply(
                left,
                right,
                node
            )

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
            evaluated_row = []

            for value in row:
                evaluated = self.evaluate(value)

                if self.should_expand_matrix_element(
                    evaluated
                ):
                    evaluated_row.extend(
                        np.asarray(evaluated).tolist()
                    )
                else:
                    evaluated_row.append(evaluated)

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

        function = self.context.resolve_function(
            node.name
        )

        if function is not None:
            if callable(function):
                return function(
                    self.context,
                    *arguments
                )

            if isinstance(function, UserFunction):
                return self.call_user_function(
                    node,
                    function,
                    arguments,
                )

            raise RuntimeError(
                f"Invalid function '{node.name}'",
                node.line,
                node.column,
            )
        
        # Otherwise treat as indexing
        try:
            target = self.context.get_variable(
                node.name
            )
        except Exception as error:
            raise RuntimeError(
                f"Undefined function '{node.name}'",
                node.line,
                node.column,
            ) from error

        indices = self.coerce_indices(arguments)

        return target[self.index_key(indices)]

    def call_user_function(
        self,
        node,
        function,
        arguments,
    ):
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

        local_context.current_source_path = (
            function.source_path
            or self.context.current_source_path
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

        self.context.push_file_functions(
            function.local_functions
        )

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
            self.context.call_stack.pop()

            self.context.pop_file_functions()

        if declaration.return_variable:
            return local_context.get_variable(
                declaration.return_variable
            )

        return result
    
    def visit_IndexNode(self, node):
        target = self.evaluate(node.target)

        indices = [
            int(self.evaluate(index)) - 1
            for index in node.indices
        ]

        return target[self.index_key(indices)]

    def coerce_indices(self, values):
        return [
            int(value) - 1
            for value in values
        ]

    def index_key(self, indices):
        if len(indices) == 1:
            return indices[0]

        return tuple(indices)

    def elementwise_multiply(
        self,
        left,
        right,
        node
    ):
        if (
            self.is_array_like(left)
            or self.is_array_like(right)
        ):
            left_array = np.asarray(left)
            right_array = np.asarray(right)

            if (
                left_array.ndim > 0
                and right_array.ndim > 0
                and left_array.shape != right_array.shape
            ):
                raise RuntimeError(
                    "Element-wise multiplication requires "
                    "operands to have the same size",
                    node.line,
                    node.column
                )

            return left_array * right_array

        return left * right

    def is_array_like(self, value):
        return isinstance(
            value,
            (
                np.ndarray,
                list,
                tuple,
            )
        )

    def should_expand_matrix_element(self, value):
        if isinstance(value, (str, SymbolicValue)):
            return False

        if not self.is_array_like(value):
            return False

        return np.asarray(value).ndim == 1
    
    def visit_FunctionDeclarationNode(self, node):
        if self.context.functions.is_builtin(
            node.name
        ):
            raise RuntimeError(
                f"Cannot redefine built-in function "
                f"'{node.name}'"
            )

        function = self.context.get_same_file_function(
            node.name
        )

        if (
            function is None
            or function.declaration is not node
        ):
            function = UserFunction(
                node,
                self.context,
                self.context.current_source_path,
            )

        self.context.functions.register(
            node.name,
            function
        )

        return None
    
    def visit_ReturnNode(self, node):
        value = self.evaluate(node.value)

        raise ReturnException(value)

    def visit_SymsNode(self, node):
        for name in node.names:
            self.context.set_variable(
                name,
                SymbolicValue(name)
            )

        return None
    
    def visit_TransposeNode(self, node):
        operand = self.evaluate(
            node.operand
        )

        array = np.asarray(operand)

        if array.ndim == 0:
            return np.conjugate(operand)

        if array.ndim == 1:
            return np.conjugate(array).reshape(-1, 1)

        return np.conjugate(array).T

    def should_store_ans(
        self,
        statement,
        result
    ):
        return (
            result is not None
            and not isinstance(
                statement,
                (
                    AssignmentNode,
                    FunctionDeclarationNode,
                    SymsNode,
                )
            )
        )

    def has_symbolic_operand(
        self,
        left,
        right
    ):
        return (
            isinstance(left, SymbolicValue)
            or isinstance(left, SymbolicEquation)
            or isinstance(right, SymbolicValue)
            or isinstance(right, SymbolicEquation)
        )

    def symbolic_binary_operation(
        self,
        left,
        operator,
        right
    ):
        operators = {
            TokenType.PLUS: "+",
            TokenType.MINUS: "-",
            TokenType.STAR: "*",
            TokenType.SLASH: "/",
            TokenType.CARET: "^",
            TokenType.DOTSTAR: ".*",
            TokenType.DOTSLASH: "./",
            TokenType.DOTCARET: ".^",
        }

        if operator == TokenType.EQEQ:
            return SymbolicEquation(
                self.symbolic_text(left),
                self.symbolic_text(right)
            )

        if operator not in operators:
            raise RuntimeError(
                f"Unsupported symbolic operator "
                f"{operator}"
            )

        return SymbolicValue(
            f"{self.symbolic_text(left)} "
            f"{operators[operator]} "
            f"{self.symbolic_text(right)}"
        )

    def symbolic_unary_operation(
        self,
        operator,
        value
    ):
        if operator == TokenType.PLUS:
            return value

        if operator == TokenType.MINUS:
            return SymbolicValue(
                f"-{self.symbolic_text(value)}"
            )

        raise RuntimeError(
            f"Unsupported symbolic unary operator "
            f"{operator}"
        )

    def symbolic_text(self, value):
        if isinstance(value, SymbolicValue):
            return str(value)

        if isinstance(value, SymbolicEquation):
            return str(value)

        if isinstance(value, float) and value.is_integer():
            return str(int(value))

        return str(value)
