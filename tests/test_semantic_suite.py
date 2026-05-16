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
