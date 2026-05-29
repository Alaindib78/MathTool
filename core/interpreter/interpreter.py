import numpy as np
from itertools import product

from core.ast.nodes import (
    ProgramNode,
    NumberNode,
    StringNode,
    IdentifierNode,
    BinaryOpNode,
    UnaryOpNode,
    AssignmentNode,
    MultiAssignmentTargetNode,
    IfNode,
    WhileNode,
    RangeNode,
    ColonNode,
    EndKeywordNode,
    MatrixNode,
    ForNode,
    FunctionCallNode,
    AnonymousFunctionNode,
    FieldAccessNode,
    IndexAccessNode,
    NameValueNode,
    FunctionDeclarationNode,
    ReturnNode,
    BreakNode,
    ContinueNode,
    SymsNode,
    TransposeNode,
)
from core.lexer.token import TokenType
from core.runtime.user_function import UserFunction
from core.runtime.function_resolver import (
    build_user_functions,
    top_level_function_declarations,
)
from core.interpreter.return_exception import (
    BreakException,
    ContinueException,
    ReturnException,
)
from core.errors.errors import RuntimeError
from core.control import is_lti_model
from core.calculus import FunctionHandle
from core.runtime.call_stack import CallFrame
from core.runtime.symbolic import (
    NameValueOption,
    SymbolicEquation,
    SymbolicValue,
    is_symbolic,
    symbolic_equal,
    sympy_text,
    to_sympy_expression,
)
from core.runtime.struct import (
    MatlabStruct,
    is_struct,
    missing_field_message,
)
from core.runtime.formatting import (
    format_assignment,
    format_value,
    output_suffix,
)

class Interpreter:
    def __init__(self, context):
        self.context = context
        self.end_value_stack = []

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
                result = self.statement_result(statement)

            return result
        except ReturnException as error:
            raise RuntimeError(
                "'return' can only be used inside a function"
            ) from error
        except BreakException as error:
            raise RuntimeError(
                "'break' can only be used inside a loop"
            ) from error
        except ContinueException as error:
            raise RuntimeError(
                "'continue' can only be used inside a loop"
            ) from error
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

    def visit_AnonymousFunctionNode(self, node):
        return FunctionHandle(
            node.parameters,
            node.body,
            self.context,
        )

    def visit_AssignmentNode(self, node):
        if isinstance(
            node.target,
            MultiAssignmentTargetNode,
        ):
            return self.assign_multiple(node)

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

            self.assign_indexed_target(
                target,
                node.target.arguments,
                value,
                node,
            )

            return value

        if isinstance(node.target, FieldAccessNode):
            self.assign_field(
                node.target,
                value,
            )

            return value

        if isinstance(node.target, IndexAccessNode):
            self.assign_indexed_expression(
                node.target,
                value,
            )

            return value

        raise RuntimeError(
            "Invalid assignment target",
            node.line,
            node.column
        )

    def statement_result(self, statement):
        result = self.evaluate(statement)

        if self.should_store_ans(
            statement,
            result,
        ):
            self.context.set_variable(
                "ans",
                result,
            )

        if self.should_auto_display(
            statement,
            result,
        ):
            self.display_statement_result(
                statement,
                result,
            )

        return result

    def should_auto_display(self, statement, result):
        if result is None:
            return False

        if getattr(statement, "suppress_output", False):
            return False

        if self.context.output_callback is None:
            return False

        return not isinstance(
            statement,
            (
                FunctionDeclarationNode,
                IfNode,
                WhileNode,
                ForNode,
                ReturnNode,
                BreakNode,
                ContinueNode,
                SymsNode,
            ),
        )

    def display_statement_result(self, statement, result):
        if isinstance(statement, AssignmentNode):
            name = self.assignment_display_name(
                statement.target,
            )

            if name is not None:
                text = format_assignment(
                    name,
                    result,
                    self.context.display_format,
                )
            else:
                text = format_value(
                    result,
                    self.context.display_format,
                )
        else:
            text = format_value(
                result,
                self.context.display_format,
            )

        self.context.output_callback(
            text + output_suffix(
                self.context.display_format,
            )
        )

    def assignment_display_name(self, target):
        if isinstance(target, IdentifierNode):
            return target.name

        if isinstance(target, MultiAssignmentTargetNode):
            return (
                "["
                + ", ".join(
                    item.name
                    for item in target.targets
                )
                + "]"
            )

        if isinstance(target, FunctionCallNode):
            return target.name

        return None

    def assign_multiple(self, node):
        expected_count = len(node.target.targets)

        if isinstance(node.value, FunctionCallNode):
            value = self.evaluate_function_call(
                node.value,
                expected_count,
            )
        else:
            value = self.evaluate(node.value)

        values = self.values_for_multi_assignment(
            value,
            expected_count,
            node,
        )

        for target, assigned_value in zip(
            node.target.targets,
            values,
        ):
            self.context.set_variable(
                target.name,
                assigned_value,
            )

        return tuple(values)

    def visit_UnaryOpNode(self, node):
        value = self.evaluate(node.operand)

        if is_symbolic(value):
            return self.symbolic_unary_operation(
                node.operator,
                value
        )

        if node.operator == TokenType.MINUS:
            if self.is_numeric_array_like(value):
                return -np.asarray(value)

            return -value

        if node.operator == TokenType.PLUS:
            if self.is_numeric_array_like(value):
                return +np.asarray(value)

            return +value
        
        if node.operator == TokenType.NOT:
            result = np.logical_not(value)

            if isinstance(result, np.generic):
                return result.item()

            return result

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
            if self.has_numeric_array_operand(left, right):
                return self.numeric_array_binary_operation(
                    left,
                    right,
                    np.add,
                )

            return left + right

        if operator == TokenType.MINUS:
            if self.has_numeric_array_operand(left, right):
                return self.numeric_array_binary_operation(
                    left,
                    right,
                    np.subtract,
                )

            return left - right

#        if operator == TokenType.STAR:
#            return left * right
        if operator == TokenType.STAR:
            if self.has_numeric_array_operand(left, right):
                return self.numeric_array_multiply(
                    left,
                    right,
                )

            return left * right
        
        if operator == TokenType.SLASH:
            if self.has_numeric_array_operand(left, right):
                return self.numeric_array_divide(
                    left,
                    right,
                )

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
            if self.has_numeric_array_operand(left, right):
                return self.numeric_array_divide(
                    left,
                    right,
                )

            return left / right

        if operator == TokenType.DOTCARET:
            if self.has_numeric_array_operand(left, right):
                return self.numeric_array_binary_operation(
                    left,
                    right,
                    np.power,
                )

            return left ** right

        if operator == TokenType.MODULO:
            if self.has_numeric_array_operand(left, right):
                return self.numeric_array_binary_operation(
                    left,
                    right,
                    np.mod,
                )

            return left % right

        if operator == TokenType.CARET:
            if self.has_numeric_array_operand(left, right):
                return self.numeric_array_binary_operation(
                    left,
                    right,
                    np.power,
                )

            return left ** right
        
        if operator == TokenType.EQEQ:
            if self.has_numeric_array_operand(left, right):
                return self.numeric_array_binary_operation(
                    left,
                    right,
                    np.equal,
                )

            return left == right

        if operator == TokenType.NEQ:
            if self.has_numeric_array_operand(left, right):
                return self.numeric_array_binary_operation(
                    left,
                    right,
                    np.not_equal,
                )

            return left != right

        if operator == TokenType.LT:
            if self.has_numeric_array_operand(left, right):
                return self.numeric_array_binary_operation(
                    left,
                    right,
                    np.less,
                )

            return left < right

        if operator == TokenType.GT:
            if self.has_numeric_array_operand(left, right):
                return self.numeric_array_binary_operation(
                    left,
                    right,
                    np.greater,
                )

            return left > right

        if operator == TokenType.LTE:
            if self.has_numeric_array_operand(left, right):
                return self.numeric_array_binary_operation(
                    left,
                    right,
                    np.less_equal,
                )

            return left <= right

        if operator == TokenType.GTE:
            if self.has_numeric_array_operand(left, right):
                return self.numeric_array_binary_operation(
                    left,
                    right,
                    np.greater_equal,
                )

            return left >= right

        if operator == TokenType.AND:
            if (
                self.is_array_like(left)
                or self.is_array_like(right)
            ):
                return np.logical_and(left, right)

            return left and right

        if operator == TokenType.OR:
            if (
                self.is_array_like(left)
                or self.is_array_like(right)
            ):
                return np.logical_or(left, right)

            return left or right

        raise RuntimeError(
            f"Unsupported operator {operator}"
        )
    
    def visit_IfNode(self, node):
        if self.evaluate(node.condition):
            result = None

            for stmt in node.then_branch:
                result = self.statement_result(stmt)

            return result

        for condition, body in node.elseif_branches:
            if self.evaluate(condition):
                result = None

                for stmt in body:
                    result = self.statement_result(stmt)

                return result

        if node.else_branch is not None:
            result = None

            for stmt in node.else_branch:
                result = self.statement_result(stmt)

            return result

        return None
    
    def visit_RangeNode(self, node):
        start = self.evaluate(node.start)
        step = self.evaluate(node.step)
        end = self.evaluate(node.end)

        values = []

        current = start

        if step == 0:
            raise RuntimeError(
                "Range step cannot be zero",
                node.line,
                node.column,
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
            try:
                for stmt in node.body:
                    result = self.statement_result(stmt)
            except ContinueException:
                continue
            except BreakException:
                break

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

            try:
                for stmt in node.body:
                    result = self.statement_result(stmt)
            except ContinueException:
                continue
            except BreakException:
                break

        return result
    
#    def visit_FunctionCallNode(self, node):
#        function = self.context.functions.get(node.name)
#
#        arguments = [self.evaluate(arg) for arg in node.arguments]
#
#        return function(self.context, *arguments)

    def visit_FunctionCallNode(self, node):
        return self.evaluate_function_call(node)

    def visit_FieldAccessNode(self, node):
        target = self.evaluate(node.target)

        if is_lti_model(target):
            return target.get_property(node.field_name)

        if hasattr(target, "get_property") and callable(target.get_property):
            return target.get_property(node.field_name)

        if not is_struct(target):
            raise RuntimeError(
                f"Cannot access field '{node.field_name}' "
                "on non-struct value",
                node.line,
                node.column,
            )

        if node.field_name not in target:
            raise RuntimeError(
                missing_field_message(node.field_name),
                node.line,
                node.column,
            )

        return target[node.field_name]

    def visit_IndexAccessNode(self, node):
        target = self.evaluate(node.target)

        return self.evaluate_indexed_target(
            target,
            node.arguments,
            node,
        )

    def evaluate_function_call(
        self,
        node,
        expected_output_count=None,
    ):
        function = self.context.resolve_function(
            node.name
        )

        if function is not None:
            arguments = [
                self.evaluate(arg)
                for arg in node.arguments
            ]

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
                    expected_output_count,
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

        if (
            expected_output_count is not None
            and expected_output_count > 1
        ):
            raise RuntimeError(
                "Indexed expressions do not support "
                "multiple outputs",
                node.line,
                node.column,
            )

        if callable(target):
            arguments = [
                self.evaluate(arg)
                for arg in node.arguments
            ]

            try:
                return target(*arguments)
            except Exception as error:
                raise RuntimeError(
                    str(error),
                    node.line,
                    node.column,
                ) from error

        return self.evaluate_indexed_target(
            target,
            node.arguments,
            node,
        )

    def assign_field(
        self,
        node,
        value,
    ):
        try:
            target_value = self.evaluate(node.target)
        except Exception:
            target_value = None

        if is_lti_model(target_value):
            target_value.set_property(
                node.field_name,
                value,
            )
            return

        target = self.struct_for_field_write(
            node.target,
            node.line,
            node.column,
        )

        target[node.field_name] = value

    def struct_for_field_write(
        self,
        node,
        line,
        column,
    ):
        if isinstance(node, IdentifierNode):
            try:
                value = self.context.get_variable(
                    node.name
                )
            except Exception:
                value = MatlabStruct()

                self.context.set_variable(
                    node.name,
                    value,
                )

            if not is_struct(value):
                raise RuntimeError(
                    f"Cannot assign field on non-struct "
                    f"value '{node.name}'",
                    line,
                    column,
                )

            return value

        if isinstance(node, FieldAccessNode):
            parent = self.struct_for_field_write(
                node.target,
                line,
                column,
            )

            if node.field_name not in parent:
                parent[node.field_name] = MatlabStruct()

            value = parent[node.field_name]

            if not is_struct(value):
                raise RuntimeError(
                    f"Cannot assign field on non-struct "
                    f"field '{node.field_name}'",
                    line,
                    column,
                )

            return value

        if isinstance(node, FunctionCallNode):
            return self.indexed_struct_for_field_write(
                node.name,
                node.arguments,
                line,
                column,
            )

        if isinstance(node, IndexAccessNode):
            target = self.evaluate(node.target)
            indices = self.coerce_indices([
                self.evaluate(arg)
                for arg in node.arguments
            ])

            return self.ensure_indexed_struct(
                target,
                indices,
                line,
                column,
            )

        raise RuntimeError(
            "Invalid field assignment target",
            line,
            column,
        )

    def indexed_struct_for_field_write(
        self,
        name,
        arguments,
        line,
        column,
    ):
        indices = self.coerce_indices([
            self.evaluate(arg)
            for arg in arguments
        ])

        if len(indices) != 1:
            raise RuntimeError(
                "Struct array field assignment supports "
                "one index",
                line,
                column,
            )

        try:
            target = self.context.get_variable(name)
        except Exception:
            target = []
            self.context.set_variable(name, target)

        return self.ensure_indexed_struct(
            target,
            indices,
            line,
            column,
        )

    def ensure_indexed_struct(
        self,
        target,
        indices,
        line,
        column,
    ):
        if len(indices) != 1:
            raise RuntimeError(
                "Struct array field assignment supports "
                "one index",
                line,
                column,
            )

        index = indices[0]

        if index < 0:
            raise RuntimeError(
                "Index must be positive",
                line,
                column,
            )

        if not isinstance(target, list):
            raise RuntimeError(
                "Cannot assign field on indexed non-struct value",
                line,
                column,
            )

        while len(target) <= index:
            target.append(None)

        if target[index] is None:
            target[index] = MatlabStruct()

        if not is_struct(target[index]):
            raise RuntimeError(
                "Cannot assign field on indexed non-struct value",
                line,
                column,
            )

        return target[index]

    def assign_indexed_expression(
        self,
        node,
        value,
    ):
        target = self.evaluate(node.target)

        self.assign_indexed_target(
            target,
            node.arguments,
            value,
            node,
        )

    def evaluate_indexed_target(
        self,
        target,
        arguments,
        node,
    ):
        if not arguments:
            raise RuntimeError(
                "Indexed expression requires at least one index",
                node.line,
                node.column,
            )

        array = self.indexable_array(
            target,
            node,
        )

        if len(arguments) == 1:
            return self.evaluate_linear_index(
                array,
                arguments[0],
                node,
            )

        array = self.array_for_subscript_count(
            array,
            len(arguments),
            node,
        )

        return self.evaluate_subscript_index(
            array,
            arguments,
            node,
        )

    def assign_indexed_target(
        self,
        target,
        arguments,
        value,
        node,
    ):
        if not arguments:
            raise RuntimeError(
                "Indexed assignment requires at least one index",
                node.line,
                node.column,
            )

        array = self.indexable_array(
            target,
            node,
        )

        if len(arguments) == 1:
            coords, shape, _ = self.linear_index_coords(
                array,
                arguments[0],
                node,
            )
        else:
            array = self.array_for_subscript_count(
                array,
                len(arguments),
                node,
            )
            coords, shape = self.subscript_index_coords(
                array,
                arguments,
                node,
            )

        self.assign_coords(
            target,
            array,
            coords,
            shape,
            value,
            node,
        )

    def indexable_array(self, target, node):
        array = np.asarray(target)

        if array.ndim == 0:
            raise RuntimeError(
                "Cannot index scalar value",
                node.line,
                node.column,
            )

        return array

    def array_for_subscript_count(
        self,
        array,
        subscript_count,
        node,
    ):
        if array.ndim == 1 and subscript_count == 2:
            return array.reshape(1, -1)

        if subscript_count > array.ndim:
            raise RuntimeError(
                "Too many indices for array",
                node.line,
                node.column,
            )

        return array

    def evaluate_linear_index(
        self,
        array,
        argument,
        node,
    ):
        coords, shape, is_logical = self.linear_index_coords(
            array,
            argument,
            node,
        )

        values = np.array(
            [
                array[coord]
                for coord in coords
            ]
        )

        if shape == ():
            return values[0].item() if hasattr(values[0], "item") else values[0]

        if isinstance(argument, ColonNode) or is_logical:
            return values.reshape(-1, 1)

        return values.reshape(shape, order="F")

    def linear_index_coords(
        self,
        array,
        argument,
        node,
    ):
        if isinstance(argument, ColonNode):
            indices = np.arange(array.size)

            return self.coords_from_linear_indices(
                array,
                indices,
            ), (array.size, 1), False

        value = self.evaluate_subscript_value(
            argument,
            array.size,
        )

        if self.is_logical_subscript(value):
            mask = np.asarray(value, dtype=bool)

            if mask.size != array.size:
                raise RuntimeError(
                    "Logical index mask must have the same "
                    "number of elements as the indexed array",
                    node.line,
                    node.column,
                )

            indices = np.flatnonzero(
                mask.reshape(-1, order="F")
            )

            return self.coords_from_linear_indices(
                array,
                indices,
            ), (len(indices), 1), True

        indices, shape, is_scalar = self.numeric_indices(
            value,
            array.size,
            node,
        )

        return self.coords_from_linear_indices(
            array,
            indices,
        ), (() if is_scalar else shape), False

    def evaluate_subscript_index(
        self,
        array,
        arguments,
        node,
    ):
        index_arrays, scalar_flags = self.subscript_indices(
            array,
            arguments,
            node,
        )

        selected = array[np.ix_(*index_arrays)]

        if all(scalar_flags):
            value = selected.reshape(-1)[0]
            return value.item() if hasattr(value, "item") else value

        if len(arguments) == 2:
            if scalar_flags[0] and not scalar_flags[1]:
                return selected.reshape(-1)

            if not scalar_flags[0] and scalar_flags[1]:
                return selected.reshape(-1, 1)

            return selected

        squeeze_axes = tuple(
            index
            for index, is_scalar in enumerate(scalar_flags)
            if is_scalar
        )

        if squeeze_axes:
            return np.squeeze(
                selected,
                axis=squeeze_axes,
            )

        return selected

    def subscript_index_coords(
        self,
        array,
        arguments,
        node,
    ):
        index_arrays, _ = self.subscript_indices(
            array,
            arguments,
            node,
        )

        coords = [
            tuple(reversed(reversed_coord))
            for reversed_coord in product(
                *reversed(index_arrays)
            )
        ]

        return coords, tuple(
            len(indices)
            for indices in index_arrays
        )

    def subscript_indices(
        self,
        array,
        arguments,
        node,
    ):
        index_arrays = []
        scalar_flags = []

        for dimension, argument in enumerate(arguments):
            end_value = array.shape[dimension]

            if isinstance(argument, ColonNode):
                index_arrays.append(
                    np.arange(end_value)
                )
                scalar_flags.append(False)
                continue

            value = self.evaluate_subscript_value(
                argument,
                end_value,
            )

            if self.is_logical_subscript(value):
                mask = np.asarray(value, dtype=bool)

                if mask.size != end_value:
                    raise RuntimeError(
                        "Logical subscript must match the "
                        "dimension length",
                        node.line,
                        node.column,
                    )

                index_arrays.append(
                    np.flatnonzero(
                        mask.reshape(-1, order="F")
                    )
                )
                scalar_flags.append(False)
                continue

            indices, _, is_scalar = self.numeric_indices(
                value,
                end_value,
                node,
            )
            index_arrays.append(indices)
            scalar_flags.append(is_scalar)

        return index_arrays, scalar_flags

    def evaluate_subscript_value(
        self,
        node,
        end_value,
    ):
        self.end_value_stack.append(end_value)

        try:
            return self.evaluate(node)
        finally:
            self.end_value_stack.pop()

    def numeric_indices(
        self,
        value,
        end_value,
        node,
    ):
        if isinstance(value, np.ndarray):
            values = value.reshape(-1, order="F")
            shape = value.shape
            is_scalar = value.ndim == 0
        elif isinstance(value, (list, tuple)):
            values = np.asarray(value).reshape(-1, order="F")
            shape = np.asarray(value).shape
            is_scalar = False
        else:
            values = np.asarray([value])
            shape = ()
            is_scalar = True

        indices = []

        for raw_value in values:
            index = self.one_based_index(
                raw_value,
                end_value,
                node,
            )
            indices.append(index)

        return (
            np.asarray(indices, dtype=int),
            shape,
            is_scalar,
        )

    def one_based_index(
        self,
        value,
        end_value,
        node,
    ):
        if isinstance(value, np.generic):
            value = value.item()

        if isinstance(value, bool):
            raise RuntimeError(
                "Logical values must be used as logical masks",
                node.line,
                node.column,
            )

        try:
            numeric_value = float(value)
        except (TypeError, ValueError) as error:
            raise RuntimeError(
                "Array indices must be positive integers "
                "or logical values",
                node.line,
                node.column,
            ) from error

        if not numeric_value.is_integer():
            raise RuntimeError(
                "Array indices must be positive integers",
                node.line,
                node.column,
            )

        index = int(numeric_value)

        if index < 1 or index > end_value:
            raise RuntimeError(
                f"Index {index} is out of bounds "
                f"for dimension with size {end_value}",
                node.line,
                node.column,
            )

        return index - 1

    def is_logical_subscript(self, value):
        if isinstance(value, (bool, np.bool_)):
            return True

        if isinstance(value, np.ndarray):
            return np.issubdtype(value.dtype, np.bool_)

        if isinstance(value, (list, tuple)):
            array = np.asarray(value)
            return np.issubdtype(array.dtype, np.bool_)

        return False

    def coords_from_linear_indices(
        self,
        array,
        indices,
    ):
        if len(indices) == 0:
            return []

        coords = np.unravel_index(
            indices,
            array.shape,
            order="F",
        )

        return list(zip(*coords))

    def assign_coords(
        self,
        target,
        array,
        coords,
        shape,
        value,
        node,
    ):
        if not coords:
            return

        values = self.assignment_values(
            value,
            len(coords),
            node,
        )

        for coord, assigned_value in zip(coords, values):
            if isinstance(target, list) and len(coord) == 1:
                target[coord[0]] = assigned_value
            else:
                array[coord] = assigned_value

    def assignment_values(
        self,
        value,
        count,
        node,
    ):
        if self.is_scalar_value(value):
            return [value] * count

        values = np.asarray(value).reshape(-1, order="F")

        if values.size != count:
            raise RuntimeError(
                "Indexed assignment dimensions do not match",
                node.line,
                node.column,
            )

        return values.tolist()

    def is_scalar_value(self, value):
        if isinstance(value, str):
            return True

        if isinstance(value, np.ndarray):
            return value.ndim == 0

        return not isinstance(value, (list, tuple))

    def call_user_function(
        self,
        node,
        function,
        arguments,
        expected_output_count=None,
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
                result = local_interpreter.statement_result(
                    stmt
                )

        except ReturnException as ret:
            if ret.has_value:
                return ret.value

            if declaration.return_variables:
                return self.user_function_outputs(
                    declaration,
                    local_context,
                    expected_output_count,
                    node,
                )

            return None
        except BreakException as error:
            raise RuntimeError(
                "'break' can only be used inside a loop"
            ) from error
        except ContinueException as error:
            raise RuntimeError(
                "'continue' can only be used inside a loop"
            ) from error
        finally:
            self.context.call_stack.pop()

            self.context.pop_file_functions()

        if declaration.return_variables:
            return self.user_function_outputs(
                declaration,
                local_context,
                expected_output_count,
                node,
            )

        return result

    def user_function_outputs(
        self,
        declaration,
        local_context,
        expected_output_count,
        node,
    ):
        output_names = declaration.return_variables

        if expected_output_count is None:
            expected_output_count = 1

        if expected_output_count > len(output_names):
            raise RuntimeError(
                f"Function '{node.name}' returns "
                f"{len(output_names)} value(s), but "
                f"{expected_output_count} were requested",
                node.line,
                node.column,
            )

        values = [
            local_context.get_variable(name)
            for name in output_names[:expected_output_count]
        ]

        if expected_output_count == 1:
            return values[0]

        return tuple(values)

    def values_for_multi_assignment(
        self,
        value,
        expected_count,
        node,
    ):
        if expected_count == 1:
            return [value]

        if isinstance(value, np.ndarray):
            values = value.tolist()
        elif isinstance(value, (list, tuple)):
            values = list(value)
        else:
            raise RuntimeError(
                "Right-hand side does not provide "
                "multiple values",
                node.line,
                node.column,
            )

        if len(values) < expected_count:
            raise RuntimeError(
                f"Expected {expected_count} values, "
                f"got {len(values)}",
                node.line,
                node.column,
            )

        if len(values) > expected_count:
            raise RuntimeError(
                f"Expected {expected_count} values, "
                f"got {len(values)}",
                node.line,
                node.column,
            )

        return values

    def visit_ColonNode(self, node):
        raise RuntimeError(
            "Colon ':' can only be used in an indexing expression",
            node.line,
            node.column,
        )

    def visit_EndKeywordNode(self, node):
        if not self.end_value_stack:
            raise RuntimeError(
                "'end' can only be used in an indexing expression",
                node.line,
                node.column,
            )

        return self.end_value_stack[-1]
    
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

    def has_numeric_array_operand(self, left, right):
        return (
            self.is_numeric_array_like(left)
            or self.is_numeric_array_like(right)
        )

    def is_numeric_array_like(self, value):
        if not isinstance(value, (np.ndarray, list, tuple)):
            return False

        try:
            array = np.asarray(value)
        except (TypeError, ValueError):
            return False

        return np.issubdtype(array.dtype, np.number)

    def numeric_array_binary_operation(
        self,
        left,
        right,
        operation,
    ):
        result = operation(
            np.asarray(left),
            np.asarray(right),
        )

        return self.normalize_numpy_result(result)

    def numeric_array_multiply(self, left, right):
        left_array = np.asarray(left)
        right_array = np.asarray(right)

        if left_array.ndim > 0 and right_array.ndim > 0:
            result = left_array @ right_array
        else:
            result = left_array * right_array

        return self.normalize_numpy_result(result)

    def numeric_array_divide(self, left, right):
        right_array = np.asarray(right)

        if np.any(right_array == 0):
            raise RuntimeError(
                "Division by zero"
            )

        result = np.asarray(left) / right_array

        return self.normalize_numpy_result(result)

    def normalize_numpy_result(self, value):
        if isinstance(value, np.generic):
            return value.item()

        if isinstance(value, np.ndarray) and value.ndim == 0:
            return value.item()

        return value

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
        if isinstance(value, str) or is_symbolic(value):
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
        if node.value is None:
            raise ReturnException(
                has_value=False,
            )

        value = self.evaluate(node.value)

        raise ReturnException(value)

    def visit_BreakNode(self, node):
        raise BreakException()

    def visit_ContinueNode(self, node):
        raise ContinueException()

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
                    IfNode,
                    WhileNode,
                    ForNode,
                    ReturnNode,
                    BreakNode,
                    ContinueNode,
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
            is_symbolic(left)
            or is_symbolic(right)
        )

    def symbolic_binary_operation(
        self,
        left,
        operator,
        right
    ):
        left_expression = to_sympy_expression(left)
        right_expression = to_sympy_expression(right)

        if operator == TokenType.EQEQ:
            return SymbolicEquation(
                left_expression,
                right_expression,
            )

        if operator == TokenType.PLUS:
            return SymbolicValue(
                left_expression + right_expression
            )

        if operator == TokenType.MINUS:
            return SymbolicValue(
                left_expression - right_expression
            )

        if operator in (TokenType.STAR, TokenType.DOTSTAR):
            return SymbolicValue(
                left_expression * right_expression
            )

        if operator in (TokenType.SLASH, TokenType.DOTSLASH):
            return SymbolicValue(
                left_expression / right_expression
            )

        if operator in (TokenType.CARET, TokenType.DOTCARET):
            return SymbolicValue(
                left_expression ** right_expression
            )

        if operator == TokenType.NEQ:
            return not (
                symbolic_equal(
                    left_expression,
                    right_expression,
                )
            )

        raise RuntimeError(
            f"Unsupported symbolic operator "
            f"{operator}"
        )

    def symbolic_unary_operation(
        self,
        operator,
        value
    ):
        expression = to_sympy_expression(value)

        if operator == TokenType.PLUS:
            return SymbolicValue(expression)

        if operator == TokenType.MINUS:
            return SymbolicValue(-expression)

        if operator == TokenType.NOT:
            raise RuntimeError(
                f"Unsupported symbolic operator "
                f"{operator}"
            )

        raise RuntimeError(
            f"Unsupported symbolic unary operator "
            f"{operator}"
        )

    def symbolic_text(self, value):
        return sympy_text(value)
