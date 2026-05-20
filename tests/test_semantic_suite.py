import pytest

from core.errors.errors import SemanticError


def test_semantic_analyzer_accepts_valid_program(parse):
    from core.semantic.semantic_analyzer import SemanticAnalyzer

    program = parse(
        """
function y = square(x)
    y = x ^ 2;
end

values = 1:3;
total = 0;
for i = values
    total = total + i;
end

answer = square(total);
"""
    )

    SemanticAnalyzer().analyze(program)


def test_semantic_analyzer_accepts_return_break_and_continue(parse):
    from core.semantic.semantic_analyzer import SemanticAnalyzer

    program = parse(
        """
function y = find_first(values)
    y = 0;

    for i = 1:5
        if i == 2
            continue;
        end

        if i == 4
            y = i;
            break;
        end
    end

    return;
end
"""
    )

    SemanticAnalyzer().analyze(program)


def test_semantic_analyzer_rejects_return_outside_function(parse):
    from core.semantic.semantic_analyzer import SemanticAnalyzer

    program = parse("return;")

    with pytest.raises(SemanticError) as error:
        SemanticAnalyzer().analyze(program)

    assert "'return' can only be used inside a function" in str(
        error.value
    )


def test_semantic_analyzer_rejects_break_outside_loop(parse):
    from core.semantic.semantic_analyzer import SemanticAnalyzer

    program = parse("break;")

    with pytest.raises(SemanticError) as error:
        SemanticAnalyzer().analyze(program)

    assert "'break' can only be used inside a loop" in str(
        error.value
    )


def test_semantic_analyzer_rejects_break_inside_function_declared_in_loop(parse):
    from core.semantic.semantic_analyzer import SemanticAnalyzer

    program = parse(
        """
for i = 1:2
    function y = bad()
        break;
    end
end
"""
    )

    with pytest.raises(SemanticError) as error:
        SemanticAnalyzer().analyze(program)

    assert "'break' can only be used inside a loop" in str(
        error.value
    )


def test_semantic_analyzer_rejects_continue_outside_loop(parse):
    from core.semantic.semantic_analyzer import SemanticAnalyzer

    program = parse("continue;")

    with pytest.raises(SemanticError) as error:
        SemanticAnalyzer().analyze(program)

    assert "'continue' can only be used inside a loop" in str(
        error.value
    )


def test_semantic_analyzer_rejects_continue_inside_function_declared_in_loop(parse):
    from core.semantic.semantic_analyzer import SemanticAnalyzer

    program = parse(
        """
for i = 1:2
    function y = bad()
        continue;
    end
end
"""
    )

    with pytest.raises(SemanticError) as error:
        SemanticAnalyzer().analyze(program)

    assert "'continue' can only be used inside a loop" in str(
        error.value
    )


def test_semantic_analyzer_rejects_undefined_variables(parse):
    from core.semantic.semantic_analyzer import SemanticAnalyzer

    program = parse("answer = missing + 1;")

    with pytest.raises(SemanticError) as error:
        SemanticAnalyzer().analyze(program)

    assert "Undefined variable 'missing'" in str(error.value)


def test_semantic_analyzer_rejects_undefined_functions(parse):
    from core.semantic.semantic_analyzer import SemanticAnalyzer

    program = parse("answer = unknown(1);")

    with pytest.raises(SemanticError) as error:
        SemanticAnalyzer().analyze(program)

    assert "Undefined function 'unknown'" in str(error.value)


def test_semantic_analyzer_rejects_assigning_immutable_constants(parse):
    from core.semantic.semantic_analyzer import SemanticAnalyzer

    program = parse("pi = 3;")

    with pytest.raises(SemanticError) as error:
        SemanticAnalyzer().analyze(program)

    assert "Cannot assign to constant 'pi'" in str(error.value)


def test_semantic_analyzer_accepts_indexed_assignment(parse):
    from core.semantic.semantic_analyzer import SemanticAnalyzer

    program = parse(
        """
M = [1 2; 3 4];
M(1,1) = 5;
"""
    )

    SemanticAnalyzer().analyze(program)


def test_semantic_analyzer_accepts_symbolic_workflow(parse):
    from core.semantic.semantic_analyzer import SemanticAnalyzer

    program = parse(
        """
syms x
value = x;
f1 = sym('x');
kind = class(f1);
class(f1);
last = ans;
"""
    )

    SemanticAnalyzer().analyze(program)


def test_semantic_analyzer_rejects_indexed_assignment_to_undefined_target(parse):
    from core.semantic.semantic_analyzer import SemanticAnalyzer

    program = parse("M(1,1) = 5;")

    with pytest.raises(SemanticError) as error:
        SemanticAnalyzer().analyze(program)

    assert "Undefined variable 'M'" in str(error.value)


def test_semantic_analyzer_keeps_function_parameters_scoped(parse):
    from core.semantic.semantic_analyzer import SemanticAnalyzer

    program = parse(
        """
function y = increment(x)
    y = x + 1;
end

leaked = x;
"""
    )

    with pytest.raises(SemanticError) as error:
        SemanticAnalyzer().analyze(program)

    assert "Undefined variable 'x'" in str(error.value)
