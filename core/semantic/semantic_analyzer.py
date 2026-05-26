from platform import node

from core.semantic.symbol_table import (
    SymbolTable
)

from core.ast.nodes import *
from core.errors.errors import SemanticError
from core.stdlib.builtins import BUILTIN_FUNCTIONS


IMMUTABLE_CONSTANTS = {
    "pi",
    "e",
    "true",
    "false",
}


class SemanticAnalyzer:
    def __init__(self, function_exists=None):
        self.global_scope = SymbolTable()

        self.current_scope = self.global_scope

        self.function_depth = 0

        self.loop_depth = 0

        self.external_function_exists = (
            function_exists
            if function_exists is not None
            else lambda name: False
        )

        self.load_builtins()

    def set_external_function_exists(
        self,
        function_exists,
    ):
        self.external_function_exists = (
            function_exists
        )

    def load_builtins(self):
        builtin_functions = BUILTIN_FUNCTIONS.keys()

        for func in builtin_functions:
            self.global_scope.define(func)

        for const in IMMUTABLE_CONSTANTS:
            self.global_scope.define(const)

        self.global_scope.define("i")
        self.global_scope.define("j")
        self.global_scope.define("ans")

    def analyze(self, node):
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
            f"No semantic visit method for "
            f"{type(node).__name__}"
        )

    # ---------------------------------
    # Program
    # ---------------------------------

    def visit_ProgramNode(self, node):
        self.define_file_functions(node.statements)

        for stmt in node.statements:
            self.analyze(stmt)

    def define_file_functions(self, statements):
        for statement in statements:
            if isinstance(
                statement,
                FunctionDeclarationNode,
            ):
                self.define_function_name(statement)

    # ---------------------------------
    # Literals
    # ---------------------------------

    def visit_NumberNode(self, node):
        pass

    def visit_StringNode(self, node):
        pass

    # ---------------------------------
    # Variables
    # ---------------------------------

    def visit_IdentifierNode(self, node):
        if not self.current_scope.exists(
            node.name
        ):
            raise SemanticError(
                f"Undefined variable '{node.name}'"
            )

    def visit_AssignmentNode(self, node):
        if isinstance(
            node.target,
            MultiAssignmentTargetNode,
        ):
            self.visit_MultiAssignmentNode(node)
            return

        self.analyze(node.value)

        if isinstance(node.target, IdentifierNode):
            name = node.target.name

            if name in IMMUTABLE_CONSTANTS:
                raise SemanticError(
                    f"Cannot assign to constant '{name}'"
                )

            self.current_scope.define(name)
            return

        if isinstance(node.target, FunctionCallNode):
            name = node.target.name

            if name in IMMUTABLE_CONSTANTS:
                raise SemanticError(
                    f"Cannot assign to constant '{name}'"
                )

            if not self.current_scope.exists(name):
                raise SemanticError(
                    f"Undefined variable '{name}'"
                )

            if not node.target.arguments:
                raise SemanticError(
                    "Indexed assignment requires at least one index"
                )

            for arg in node.target.arguments:
                self.analyze(arg)

            return

        if isinstance(node.target, FieldAccessNode):
            self.analyze_field_assignment_target(
                node.target
            )
            return

        if isinstance(node.target, IndexAccessNode):
            self.analyze_index_assignment_target(
                node.target
            )
            return

        raise SemanticError(
            "Invalid assignment target"
        )

    def analyze_field_assignment_target(self, node):
        root = self.field_assignment_root(node)

        if root is not None:
            if root in IMMUTABLE_CONSTANTS:
                raise SemanticError(
                    f"Cannot assign to constant '{root}'"
                )

            self.current_scope.define(root)

    def field_assignment_root(self, node):
        target = node.target

        if isinstance(target, IdentifierNode):
            return target.name

        if isinstance(target, FieldAccessNode):
            return self.field_assignment_root(target)

        if isinstance(target, FunctionCallNode):
            if not target.arguments:
                raise SemanticError(
                    "Indexed assignment requires at least one index"
                )

            for arg in target.arguments:
                self.analyze(arg)

            return target.name

        if isinstance(target, IndexAccessNode):
            self.analyze_index_assignment_target(target)
            return None

        self.analyze(target)
        return None

    def analyze_index_assignment_target(self, node):
        self.analyze(node.target)

        if not node.arguments:
            raise SemanticError(
                "Indexed assignment requires at least one index"
            )

        for arg in node.arguments:
            self.analyze(arg)

    def visit_MultiAssignmentNode(self, node):
        self.analyze(node.value)

        for target in node.target.targets:
            if target.name in IMMUTABLE_CONSTANTS:
                raise SemanticError(
                    f"Cannot assign to constant "
                    f"'{target.name}'"
                )

            self.current_scope.define(target.name)

    # ---------------------------------
    # Expressions
    # ---------------------------------

    def visit_BinaryOpNode(self, node):
        self.analyze(node.left)
        self.analyze(node.right)

    def visit_UnaryOpNode(self, node):
        self.analyze(node.operand)

    def visit_TransposeNode(self, node):
        self.analyze(node.operand)

    def visit_FieldAccessNode(self, node):
        self.analyze(node.target)

    def visit_IndexAccessNode(self, node):
        self.analyze(node.target)

        for arg in node.arguments:
            self.analyze(arg)

    def visit_RangeNode(self, node):
        self.analyze(node.start)
        self.analyze(node.step)
        self.analyze(node.end)

    def visit_ColonNode(self, node):
        pass

    def visit_EndKeywordNode(self, node):
        pass

    def visit_MatrixNode(self, node):
        for row in node.rows:
            for value in row:
                self.analyze(value)

    # ---------------------------------
    # Function Calls
    # ---------------------------------

    def visit_FunctionCallNode(self, node):
        if (
            not self.current_scope.exists(
                node.name
            )
            and not self.external_function_exists(
                node.name
            )
        ):
            raise SemanticError(
                f"Undefined function '{node.name}'"
            )

        for arg in node.arguments:
            self.analyze(arg)

    def visit_NameValueNode(self, node):
        self.analyze(node.value)

    # ---------------------------------
    # Control Flow
    # ---------------------------------

    def visit_IfNode(self, node):
        self.analyze(node.condition)

        for stmt in node.then_branch:
            self.analyze(stmt)

        for cond, body in node.elseif_branches:
            self.analyze(cond)

            for stmt in body:
                self.analyze(stmt)

        if node.else_branch:
            for stmt in node.else_branch:
                self.analyze(stmt)

    def visit_WhileNode(self, node):
        self.analyze(node.condition)

        self.loop_depth += 1

        try:
            for stmt in node.body:
                self.analyze(stmt)
        finally:
            self.loop_depth -= 1

    def visit_ForNode(self, node):
        self.analyze(node.iterable)

        loop_scope = SymbolTable(
            self.current_scope
        )

        previous_scope = self.current_scope

        self.current_scope = loop_scope

        self.loop_depth += 1

        try:
            loop_scope.define(node.variable.name)

            for stmt in node.body:
                self.analyze(stmt)
        finally:
            self.loop_depth -= 1

            self.current_scope = previous_scope

    def visit_BreakNode(self, node):
        if self.loop_depth <= 0:
            raise SemanticError(
                "'break' can only be used inside a loop",
                node.line,
                node.column,
            )

    def visit_ContinueNode(self, node):
        if self.loop_depth <= 0:
            raise SemanticError(
                "'continue' can only be used inside a loop",
                node.line,
                node.column,
            )

    # ---------------------------------
    # Functions
    # ---------------------------------

    def visit_FunctionDeclarationNode(
        self,
        node
    ):
        self.define_function_name(node)

        function_scope = SymbolTable(
            self.current_scope
        )

        previous_scope = self.current_scope
        previous_loop_depth = self.loop_depth

        self.current_scope = function_scope

        self.function_depth += 1
        self.loop_depth = 0

        try:
            for param in node.parameters:
                function_scope.define(param)

            for return_variable in node.return_variables:
                function_scope.define(return_variable)

            self.define_file_functions(node.body)

            for stmt in node.body:
                self.analyze(stmt)
        finally:
            self.function_depth -= 1
            self.loop_depth = previous_loop_depth

            self.current_scope = previous_scope

    def define_function_name(self, node):
        if node.name in BUILTIN_FUNCTIONS:
            raise SemanticError(
                f"Cannot redefine built-in function "
                f"'{node.name}'"
            )

        self.current_scope.define(node.name)

    def visit_ReturnNode(self, node):
        if self.function_depth <= 0:
            raise SemanticError(
                "'return' can only be used inside a function",
                node.line,
                node.column,
            )

        if node.value is not None:
            self.analyze(node.value)

    def visit_SymsNode(self, node):
        for name in node.names:
            self.current_scope.define(name)
