import pytest

from core.ast.nodes import (
    AssignmentNode,
    BinaryOpNode,
    BreakNode,
    ColonNode,
    ContinueNode,
    EndKeywordNode,
    FunctionCallNode,
    AnonymousFunctionNode,
    FieldAccessNode,
    IndexAccessNode,
    FunctionDeclarationNode,
    IfNode,
    MatrixNode,
    MultiAssignmentTargetNode,
    RangeNode,
    ReturnNode,
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
    assert assignment.suppress_output is True
    assert isinstance(assignment.value, BinaryOpNode)
    assert assignment.value.operator == TokenType.PLUS
    assert assignment.value.left.value == 2
    assert assignment.value.right.operator == TokenType.STAR
    assert assignment.value.right.left.value == 3
    assert assignment.value.right.right.value == 4


def test_parser_tracks_missing_semicolon_for_automatic_output(parse):
    program = parse("A = 1\nA + 2;")

    assert program.statements[0].suppress_output is False
    assert program.statements[1].suppress_output is True


def test_parser_builds_anonymous_function_node(parse):
    program = parse("f = @(x, y) x.^2 + y;")

    assignment = program.statements[0]

    assert isinstance(assignment, AssignmentNode)
    assert isinstance(assignment.value, AnonymousFunctionNode)
    assert assignment.value.parameters == ["x", "y"]
    assert isinstance(assignment.value.body, BinaryOpNode)


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


def test_parser_builds_multi_output_function_declaration_and_assignment(parse):
    program = parse(
        """
function [m, s] = stat(x)
    m = x;
    s = x + 1;
end

[ave stdev] = stat(values);
"""
    )

    function = program.statements[0]
    assignment = program.statements[1]

    assert isinstance(function, FunctionDeclarationNode)
    assert function.name == "stat"
    assert function.return_variable == "m"
    assert function.return_variables == ["m", "s"]

    assert isinstance(assignment, AssignmentNode)
    assert isinstance(
        assignment.target,
        MultiAssignmentTargetNode,
    )
    assert [
        target.name
        for target in assignment.target.targets
    ] == ["ave", "stdev"]


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


def test_parser_builds_dotted_field_assignment_and_access(parse):
    program = parse(
        """
user.address.city = 'Boston';
city = user.address.city;
grade = student.grades(2);
"""
    )

    assignment = program.statements[0]
    read_assignment = program.statements[1]
    indexed_read = program.statements[2]

    assert isinstance(assignment.target, FieldAccessNode)
    assert assignment.target.field_name == "city"
    assert assignment.target.target.field_name == "address"
    assert assignment.target.target.target.name == "user"

    assert isinstance(read_assignment.value, FieldAccessNode)
    assert read_assignment.value.field_name == "city"

    assert isinstance(indexed_read.value, IndexAccessNode)
    assert isinstance(indexed_read.value.target, FieldAccessNode)
    assert indexed_read.value.target.field_name == "grades"


def test_parser_builds_colon_and_end_indexing_arguments(parse):
    program = parse(
        """
row = A(2, :);
tail = A(end-1:end, :);
flat = A(:);
"""
    )

    row_assignment = program.statements[0]
    tail_assignment = program.statements[1]
    flat_assignment = program.statements[2]

    assert isinstance(row_assignment.value, FunctionCallNode)
    assert isinstance(row_assignment.value.arguments[1], ColonNode)

    assert isinstance(tail_assignment.value.arguments[0], RangeNode)
    assert isinstance(
        tail_assignment.value.arguments[0].start,
        BinaryOpNode,
    )
    assert isinstance(
        tail_assignment.value.arguments[0].start.left,
        EndKeywordNode,
    )
    assert isinstance(flat_assignment.value.arguments[0], ColonNode)


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


def test_parser_builds_help_command_statement(parse):
    program = parse("help eig;")

    call = program.statements[0]

    assert isinstance(call, FunctionCallNode)
    assert call.name == "help"
    assert len(call.arguments) == 1
    assert call.arguments[0].value == "eig"


def test_parser_builds_lookfor_command_statement(parse):
    program = parse("lookfor eigen;")

    call = program.statements[0]

    assert isinstance(call, FunctionCallNode)
    assert call.name == "lookfor"
    assert len(call.arguments) == 1
    assert call.arguments[0].value == "eigen"


def test_parser_builds_cwd_command_statement(parse):
    program = parse("cwd")

    call = program.statements[0]

    assert isinstance(call, FunctionCallNode)
    assert call.name == "cwd"
    assert call.arguments == []


def test_parser_builds_figure_and_close_command_statements(parse):
    program = parse(
        """
figure
close
close all
"""
    )

    figure_call = program.statements[0]
    close_call = program.statements[1]
    close_all_call = program.statements[2]

    assert isinstance(figure_call, FunctionCallNode)
    assert figure_call.name == "figure"
    assert figure_call.arguments == []
    assert close_call.name == "close"
    assert close_call.arguments == []
    assert close_all_call.name == "close"
    assert close_all_call.arguments[0].value == "all"


def test_parser_builds_axis_command_statement(parse):
    program = parse(
        """
axis
axis tight
axis auto x
axis off
"""
    )

    axis_query = program.statements[0]
    axis_tight = program.statements[1]
    axis_auto_x = program.statements[2]
    axis_off = program.statements[3]

    assert isinstance(axis_query, FunctionCallNode)
    assert axis_query.name == "axis"
    assert axis_query.arguments == []
    assert [argument.value for argument in axis_tight.arguments] == [
        "tight",
    ]
    assert [argument.value for argument in axis_auto_x.arguments] == [
        "auto",
        "x",
    ]
    assert [argument.value for argument in axis_off.arguments] == [
        "off",
    ]


def test_parser_builds_return_break_and_continue_statements(parse):
    program = parse(
        """
function y = control(x)
    y = 0;
    for i = 1:5
        if i == 2
            continue;
        elseif i == 4
            break;
        end
    end
    return;
end
"""
    )

    function = program.statements[0]
    loop = function.body[1]
    if_node = loop.body[0]

    assert isinstance(if_node.then_branch[0], ContinueNode)
    assert isinstance(if_node.elseif_branches[0][1][0], BreakNode)
    assert isinstance(function.body[-1], ReturnNode)
    assert function.body[-1].value is None


def test_parser_builds_return_statement_with_expression(parse):
    program = parse(
        """
function y = control(x)
    return x + 1;
end
"""
    )

    return_statement = program.statements[0].body[0]

    assert isinstance(return_statement, ReturnNode)
    assert isinstance(return_statement.value, BinaryOpNode)


def test_parser_raises_on_incomplete_expression():
    tokens = Lexer("A = (1 + 2;").tokenize()
    parser = Parser(tokens)

    with pytest.raises(ParserError) as error:
        parser.parse()

    assert "Expected token" in str(error.value)
