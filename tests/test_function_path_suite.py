import pytest

from core.errors.errors import SemanticError
from core.interpreter.interpreter import Interpreter
from core.lexer.lexer import Lexer
from core.parser.parser import Parser
from core.runtime.context import RuntimeContext
from core.semantic.semantic_analyzer import SemanticAnalyzer


def parse_source(source):
    return Parser(Lexer(source).tokenize()).parse()


def execute_with_context(source, context, source_path=None):
    ast = parse_source(source)

    SemanticAnalyzer(
        function_exists=context.function_exists
    ).analyze(ast)

    return Interpreter(context).evaluate(
        ast,
        source_path=source_path,
    )


def write_function(directory, name, body):
    path = directory / f"{name}.m"
    path.write_text(body, encoding="utf-8")
    return path


def test_current_working_directory_function_is_callable(tmp_path):
    write_function(
        tmp_path,
        "gcd",
        """
function y = gcd(x)
    y = x + 1;
end
""",
    )

    context = RuntimeContext()
    context.set_current_working_directory(tmp_path)

    execute_with_context(
        """
b = 4;
a = gcd(b);
""",
        context,
    )

    assert context.variables["a"] == 5


def test_function_file_can_call_sibling_function_file(tmp_path):
    write_function(
        tmp_path,
        "gcd",
        """
function y = gcd(x)
    y = x + 1;
end
""",
    )

    write_function(
        tmp_path,
        "myfile",
        """
function y = myfile(x)
    y = gcd(x);
end
""",
    )

    context = RuntimeContext()
    context.set_current_working_directory(tmp_path)

    execute_with_context(
        "a = myfile(4);",
        context,
    )

    assert context.variables["a"] == 5


def test_same_file_function_precedes_current_directory(tmp_path):
    script_path = tmp_path / "myfile.m"

    write_function(
        tmp_path,
        "pick",
        """
function y = pick()
    y = 10;
end
""",
    )

    source = """
value = pick();

function y = pick()
    y = 3;
end
"""

    script_path.write_text(source, encoding="utf-8")

    context = RuntimeContext()
    context.set_current_working_directory(tmp_path)

    execute_with_context(
        source,
        context,
        source_path=str(script_path),
    )

    assert context.variables["value"] == 3


def test_nested_function_is_available_before_its_declaration(tmp_path):
    source = """
value = outer(4);

function y = outer(x)
    y = inner(x);

    function z = inner(a)
        z = a + 1;
    end
end
"""

    context = RuntimeContext()
    context.set_current_working_directory(tmp_path)

    execute_with_context(
        source,
        context,
        source_path=str(tmp_path / "nested.m"),
    )

    assert context.variables["value"] == 5


def test_current_directory_precedes_external_search_path(tmp_path):
    current = tmp_path / "current"
    external = tmp_path / "external"
    current.mkdir()
    external.mkdir()

    write_function(
        current,
        "pick",
        """
function y = pick()
    y = 1;
end
""",
    )

    write_function(
        external,
        "pick",
        """
function y = pick()
    y = 2;
end
""",
    )

    context = RuntimeContext()
    context.set_current_working_directory(current)
    context.add_search_path(external)

    execute_with_context(
        "value = pick();",
        context,
    )

    assert context.variables["value"] == 1


def test_external_search_paths_resolve_in_configured_order(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    current = tmp_path / "current"

    first.mkdir()
    second.mkdir()
    current.mkdir()

    write_function(
        first,
        "pick",
        """
function y = pick()
    y = 1;
end
""",
    )

    write_function(
        second,
        "pick",
        """
function y = pick()
    y = 2;
end
""",
    )

    context = RuntimeContext()
    context.set_current_working_directory(current)
    context.add_search_path(first)
    context.add_search_path(second)

    execute_with_context(
        "value = pick();",
        context,
    )

    assert context.variables["value"] == 1


def test_changing_current_directory_changes_function_resolution(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"

    first.mkdir()
    second.mkdir()

    write_function(
        first,
        "pick",
        """
function y = pick()
    y = 1;
end
""",
    )

    write_function(
        second,
        "pick",
        """
function y = pick()
    y = 2;
end
""",
    )

    context = RuntimeContext()
    context.set_current_working_directory(first)

    execute_with_context(
        "first_value = pick();",
        context,
    )

    context.set_current_working_directory(second)

    execute_with_context(
        "second_value = pick();",
        context,
    )

    assert context.variables["first_value"] == 1
    assert context.variables["second_value"] == 2


def test_current_directory_precedes_previously_registered_function(tmp_path):
    current = tmp_path / "current"
    current.mkdir()

    context = RuntimeContext()
    context.set_current_working_directory(current)

    execute_with_context(
        """
function y = pick()
    y = 9;
end
""",
        context,
    )

    write_function(
        current,
        "pick",
        """
function y = pick()
    y = 1;
end
""",
    )

    execute_with_context(
        "value = pick();",
        context,
    )

    assert context.variables["value"] == 1


def test_user_function_cannot_redefine_builtin(parse):
    program = parse(
        """
function y = sin(x)
    y = x;
end
"""
    )

    with pytest.raises(SemanticError) as error:
        SemanticAnalyzer().analyze(program)

    assert "Cannot redefine built-in function 'sin'" in str(
        error.value
    )


def test_path_validation_rejects_builtin_conflicts(tmp_path):
    write_function(
        tmp_path,
        "sin",
        """
function y = sin(x)
    y = x;
end
""",
    )

    context = RuntimeContext()
    context.set_current_working_directory(tmp_path)

    with pytest.raises(Exception) as error:
        context.validate_function_paths()

    assert "conflicts with a built-in function" in str(
        error.value
    )
