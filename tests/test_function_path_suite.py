import pytest
from pathlib import Path

from core.errors.errors import RuntimeError as MathToolRuntimeError
from core.errors.errors import SemanticError
from core.interpreter.interpreter import Interpreter
from core.lexer.lexer import Lexer
from core.parser.parser import Parser
from core.runtime.context import RuntimeContext
from core.runtime.script_command import load_script_command
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


def execute_script_command(command, context, semantic=None):
    script_command = load_script_command(
        context,
        command,
    )

    assert script_command is not None

    semantic = semantic or SemanticAnalyzer(
        function_exists=context.function_exists
    )

    semantic.analyze(script_command.ast)

    return Interpreter(context).evaluate(
        script_command.ast,
        source_path=script_command.path,
    )


def write_function(directory, name, body):
    path = directory / f"{name}.m"
    path.write_text(body, encoding="utf-8")
    return path


def test_current_working_directory_function_is_callable(tmp_path):
    write_function(
        tmp_path,
        "cwd_only",
        """
function y = cwd_only(x)
    y = x + 1;
end
""",
    )

    context = RuntimeContext()
    context.set_current_working_directory(tmp_path)

    execute_with_context(
        """
b = 4;
a = cwd_only(b);
""",
        context,
    )

    assert context.variables["a"] == 5


def test_bare_script_name_runs_script_from_current_directory(tmp_path):
    write_function(
        tmp_path,
        "script_1",
        """
value = 4 + 1;
""",
    )

    context = RuntimeContext()
    context.set_current_working_directory(tmp_path)

    result = execute_script_command(
        "script_1",
        context,
    )

    assert result == 5
    assert context.variables["value"] == 5


def test_bare_script_name_uses_script_local_functions(tmp_path):
    write_function(
        tmp_path,
        "script_1",
        """
value = helper(4);

function y = helper(x)
    y = x + 1;
end
""",
    )

    context = RuntimeContext()
    context.set_current_working_directory(tmp_path)

    execute_script_command(
        "script_1",
        context,
    )

    assert context.variables["value"] == 5


def test_bare_script_name_does_not_shadow_workspace_variable(tmp_path):
    write_function(
        tmp_path,
        "script_1",
        """
value = 10;
""",
    )

    context = RuntimeContext()
    context.set_current_working_directory(tmp_path)
    context.set_variable("script_1", 7)

    assert load_script_command(
        context,
        "script_1",
    ) is None


def test_bare_script_name_ignores_function_only_file(tmp_path):
    write_function(
        tmp_path,
        "script_1",
        """
function y = script_1()
    y = 10;
end
""",
    )

    context = RuntimeContext()
    context.set_current_working_directory(tmp_path)

    assert load_script_command(
        context,
        "script_1",
    ) is None


def test_function_file_can_call_sibling_function_file(tmp_path):
    write_function(
        tmp_path,
        "sibling_only",
        """
function y = sibling_only(x)
    y = x + 1;
end
""",
    )

    write_function(
        tmp_path,
        "myfile",
        """
function y = myfile(x)
    y = sibling_only(x);
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
    script_path = tmp_path / "nested.m"

    source = """
value = outer(4);

function y = outer(x)
    y = inner(x);

    function z = inner(a)
        z = a + 1;
    end
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


def test_core_library_path_precedes_current_and_external_paths(
    tmp_path,
):
    library = tmp_path / "library"
    current = tmp_path / "current"
    external = tmp_path / "external"

    library.mkdir()
    current.mkdir()
    external.mkdir()

    write_function(
        library,
        "library_pick",
        """
function y = library_pick()
    y = 10;
end
""",
    )

    write_function(
        current,
        "library_pick",
        """
function y = library_pick()
    y = 20;
end
""",
    )

    write_function(
        external,
        "library_pick",
        """
function y = library_pick()
    y = 30;
end
""",
    )

    context = RuntimeContext()
    context.library_paths = [
        str(library.resolve())
    ]
    context.set_current_working_directory(current)
    context.add_search_path(external)

    execute_with_context(
        "value = library_pick();",
        context,
    )

    assert context.variables["value"] == 10


def test_core_library_subdirectories_are_resolved(tmp_path):
    library = tmp_path / "library"
    nested = library / "signals" / "filters"

    nested.mkdir(parents=True)

    write_function(
        nested,
        "nested_pick",
        """
function y = nested_pick()
    y = 42;
end
""",
    )

    context = RuntimeContext()
    context.library_paths = [
        str(library.resolve()),
        str((library / "signals").resolve()),
        str(nested.resolve()),
    ]
    context.set_current_working_directory(tmp_path)

    execute_with_context(
        "value = nested_pick();",
        context,
    )

    assert context.variables["value"] == 42


def test_same_file_function_precedes_core_library_path(
    tmp_path,
):
    library = tmp_path / "library"
    current = tmp_path / "current"
    script_path = current / "caller.m"

    library.mkdir()
    current.mkdir()

    write_function(
        library,
        "local_pick",
        """
function y = local_pick()
    y = 10;
end
""",
    )

    source = """
value = local_pick();

function y = local_pick()
    y = 5;
end
"""
    script_path.write_text(source, encoding="utf-8")

    context = RuntimeContext()
    context.library_paths = [
        str(library.resolve())
    ]
    context.set_current_working_directory(current)

    execute_with_context(
        source,
        context,
        source_path=str(script_path),
    )

    assert context.variables["value"] == 5


def test_builtins_precede_core_library_path(tmp_path):
    library = tmp_path / "library"
    library.mkdir()

    write_function(
        library,
        "sin",
        """
function y = sin(x)
    y = 99;
end
""",
    )

    context = RuntimeContext()
    context.library_paths = [
        str(library.resolve())
    ]

    assert context.resolve_function("sin") is (
        context.functions.get("sin")
    )


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


def test_path_validation_skips_inaccessible_directory(
    tmp_path,
    monkeypatch,
):
    context = RuntimeContext()
    context.set_current_working_directory(tmp_path)

    original_glob = Path.glob
    inaccessible_directory = tmp_path.resolve()

    def deny_glob(path, pattern):
        if path == inaccessible_directory:
            raise PermissionError("access denied")

        return original_glob(path, pattern)

    monkeypatch.setattr(Path, "glob", deny_glob)

    context.validate_function_paths()


def test_inaccessible_function_file_reports_runtime_error(
    tmp_path,
    monkeypatch,
):
    function_path = write_function(
        tmp_path,
        "blocked",
        """
function y = blocked()
    y = 1;
end
""",
    )

    context = RuntimeContext()
    context.set_current_working_directory(tmp_path)

    original_read_text = Path.read_text
    inaccessible_path = function_path.resolve()

    def deny_read_text(path, *args, **kwargs):
        if path == inaccessible_path:
            raise PermissionError("access denied")

        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", deny_read_text)

    with pytest.raises(MathToolRuntimeError) as error:
        context.resolve_function("blocked")

    assert "Function file" in str(error.value)
    assert "not accessible" in str(error.value)
