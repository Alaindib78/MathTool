import pytest

from core.ast.nodes import (
    AssignmentNode,
    BinaryOpNode,
    FunctionCallNode,
    FunctionDeclarationNode,
    IfNode,
    MatrixNode,
    RangeNode,
    SymsNode,
    UnaryOpNode,
)
from core.errors.errors import ParserError
from core.lexer.lexer import Lexer
from core.lexer.token import TokenType
from core.parser.parser import Parser


def test_parser_preserves_arithmetic_precedence(parse):
    program = parse("A = 2 + 3 * 4;")

    assignment = program.statements[0]

    assert isinstance(assignment, AssignmentNode)
    assert isinstance(assignment.value, BinaryOpNode)
    assert assignment.value.operator == TokenType.PLUS
    assert assignment.value.left.value == 2
    assert assignment.value.right.operator == TokenType.STAR
    assert assignment.value.right.left.value == 3
    assert assignment.value.right.right.value == 4


def test_parser_builds_control_flow_and_function_nodes(parse):
    program = parse(
        """
function y = classify(x)
    if x > 10
        y = 1;
    elseif x == 10
        y = 0;
    else
        y = -1;
    end
end
"""
    )

    function = program.statements[0]
    body_statement = function.body[0]

    assert isinstance(function, FunctionDeclarationNode)
    assert function.name == "classify"
    assert function.return_variable == "y"
    assert function.parameters == ["x"]
    assert isinstance(body_statement, IfNode)
    assert len(body_statement.then_branch) == 1
    assert len(body_statement.elseif_branches) == 1
    assert len(body_statement.else_branch) == 1


def test_parser_builds_range_and_matrix_literals(parse):
    program = parse(
        """
values = 1:2:5;
matrix = [1 2; -3 4];
"""
    )

    range_assignment = program.statements[0]
    matrix_assignment = program.statements[1]

    assert isinstance(range_assignment.value, RangeNode)
    assert range_assignment.value.start.value == 1
    assert range_assignment.value.step.value == 2
    assert range_assignment.value.end.value == 5

    assert isinstance(matrix_assignment.value, MatrixNode)
    assert len(matrix_assignment.value.rows) == 2
    assert isinstance(matrix_assignment.value.rows[1][0], UnaryOpNode)
    assert matrix_assignment.value.rows[1][0].operator == TokenType.MINUS


def test_parser_builds_indexed_assignment_target(parse):
    program = parse(
        """
M = [1 2; 3 4];
M(1, 2) = 9;
"""
    )

    assignment = program.statements[1]

    assert isinstance(assignment, AssignmentNode)
    assert isinstance(assignment.target, FunctionCallNode)
    assert assignment.target.name == "M"
    assert len(assignment.target.arguments) == 2
    assert assignment.value.value == 9


def test_parser_builds_matlab_logical_not(parse):
    program = parse("flag = ~false;")

    assignment = program.statements[0]

    assert isinstance(assignment, AssignmentNode)
    assert isinstance(assignment.value, UnaryOpNode)
    assert assignment.value.operator == TokenType.NOT


def test_parser_builds_syms_statement(parse):
    program = parse(
        """
syms x y
x;
"""
    )

    syms = program.statements[0]

    assert isinstance(syms, SymsNode)
    assert syms.names == ["x", "y"]
    assert len(program.statements) == 2


def test_parser_raises_on_incomplete_expression():
    tokens = Lexer("A = (1 + 2;").tokenize()
    parser = Parser(tokens)

    with pytest.raises(ParserError) as error:
        parser.parse()

    assert "Expected token" in str(error.value)
