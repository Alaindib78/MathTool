from platform import node

from core.semantic.symbol_table import (
    SymbolTable
)

from core.ast.nodes import *
from core.errors.errors import SemanticError


IMMUTABLE_CONSTANTS = {
    "pi",
    "e",
    "true",
    "false",
}


class SemanticAnalyzer:
    def __init__(self):
        self.global_scope = SymbolTable()

        self.current_scope = self.global_scope

        self.load_builtins()

    def load_builtins(self):
        builtin_functions = [
            "print",
            "println",
            "sin",
            "cos",
            "tan",
            "asin",
            "acos",
            "atan",
            "log",
            "log10",
            "floor",
            "ceil",
            "round",
            "sign",
            "sqrt",
            "abs",
            "zeros",
            "ones",
            "length",
            "size",
            "eye",
            "det",
            "inv", 
            "sum",
            "mean",
            "max",
            "min",
            "plot",
            "mod",
            "title",
            "xlabel",
            "ylabel",
            "grid",
            "sym",
            "class",
        ]

        for func in builtin_functions:
            self.global_scope.define(func)

        for const in IMMUTABLE_CONSTANTS:
            self.global_scope.define(const)

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
        for stmt in node.statements:
            self.analyze(stmt)

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
        name = node.target.name

        if name in IMMUTABLE_CONSTANTS:
            raise SemanticError(
                f"Cannot assign to constant '{name}'"
            )

        self.analyze(node.value)

        if isinstance(node.target, IdentifierNode):
            self.current_scope.define(name)
            return

        if isinstance(node.target, FunctionCallNode):
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

        raise SemanticError(
            "Invalid assignment target"
        )

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

    def visit_RangeNode(self, node):
        self.analyze(node.start)
        self.analyze(node.step)
        self.analyze(node.end)

    def visit_MatrixNode(self, node):
        for row in node.rows:
            for value in row:
                self.analyze(value)

    # ---------------------------------
    # Function Calls
    # ---------------------------------

    def visit_FunctionCallNode(self, node):
        if not self.current_scope.exists(
            node.name
        ):
            raise SemanticError(
                f"Undefined function '{node.name}'"
            )

        for arg in node.arguments:
            self.analyze(arg)

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

        for stmt in node.body:
            self.analyze(stmt)

    def visit_ForNode(self, node):
        self.analyze(node.iterable)

        loop_scope = SymbolTable(
            self.current_scope
        )

        previous_scope = self.current_scope

        self.current_scope = loop_scope

        loop_scope.define(node.variable.name)

        for stmt in node.body:
            self.analyze(stmt)

        self.current_scope = previous_scope

    # ---------------------------------
    # Functions
    # ---------------------------------

    def visit_FunctionDeclarationNode(
        self,
        node
    ):
        self.current_scope.define(node.name)

        function_scope = SymbolTable(
            self.current_scope
        )

        previous_scope = self.current_scope

        self.current_scope = function_scope

        for param in node.parameters:
            function_scope.define(param)

        if node.return_variable:
            function_scope.define(
                node.return_variable
            )

        for stmt in node.body:
            self.analyze(stmt)

        self.current_scope = previous_scope

    def visit_ReturnNode(self, node):
        self.analyze(node.value)

    def visit_SymsNode(self, node):
        for name in node.names:
            self.current_scope.define(name)
