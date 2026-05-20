from core.documentation.database import FunctionHelpDatabase
from core.documentation.parser import parse_function_help
from core.runtime.context import RuntimeContext


DOCUMENTED_SOURCE = """
function y = squareNumber(x)
% SQUARENUMBER Squares the input value.
%
%   y = SQUARENUMBER(x) returns x squared.
%
%   Example:
%       y = squareNumber(5)
%
%   See also sqrt, power
    y = x ^ 2;
end

% This comment must be ignored.

function y = undocumented(x)
    y = x;
    % This comment is not a help block.
end
"""


def test_parse_function_help_reads_immediate_matlab_comment_block():
    entries = parse_function_help(DOCUMENTED_SOURCE)

    assert len(entries) == 1

    entry = entries[0]

    assert entry.functionName == "squareNumber"
    assert entry.signature == "function y = squareNumber(x)"
    assert entry.h1Line == "SQUARENUMBER Squares the input value."
    assert "returns x squared" in entry.fullText
    assert entry.examples == ["      y = squareNumber(5)"]
    assert entry.seeAlso == ["sqrt", "power"]


def test_help_database_indexes_user_functions_and_builtins(tmp_path):
    path = tmp_path / "squareNumber.m"
    path.write_text(DOCUMENTED_SOURCE, encoding="utf-8")

    context = RuntimeContext()
    context.set_current_working_directory(tmp_path)

    entry = context.help_database.get("squareNumber")

    assert entry is not None
    assert entry.functionName == "squareNumber"
    assert entry.sourcePath == str(path.resolve())

    builtin = context.help_database.get("sqrt")

    assert builtin is not None
    assert builtin.isBuiltin is True


def test_help_database_formats_help_and_missing_topic(tmp_path):
    (tmp_path / "squareNumber.m").write_text(
        DOCUMENTED_SOURCE,
        encoding="utf-8",
    )

    context = RuntimeContext()
    context.set_current_working_directory(tmp_path)

    text = context.help_database.format_help("squareNumber")

    assert "squareNumber" in text
    assert "Signature:" in text
    assert "SQUARENUMBER Squares the input value." in text

    assert (
        context.help_database.format_help("missing")
        == "No help available for missing"
    )


def test_help_database_lookfor_searches_h1_and_body(tmp_path):
    (tmp_path / "squareNumber.m").write_text(
        DOCUMENTED_SOURCE,
        encoding="utf-8",
    )

    context = RuntimeContext()
    context.set_current_working_directory(tmp_path)

    matches = context.help_database.lookfor("squared")

    assert [
        entry.functionName
        for entry in matches
        if entry.functionName == "squareNumber"
    ] == ["squareNumber"]

    text = context.help_database.format_lookfor("squared")

    assert "squareNumber - SQUARENUMBER Squares the input value." in text


def test_help_database_reindexes_when_file_changes(tmp_path):
    path = tmp_path / "squareNumber.m"
    path.write_text(DOCUMENTED_SOURCE, encoding="utf-8")

    context = RuntimeContext()
    context.set_current_working_directory(tmp_path)

    assert "Squares the input" in (
        context.help_database.get("squareNumber").h1Line
    )

    path.write_text(
        DOCUMENTED_SOURCE.replace(
            "Squares the input value.",
            "Raises the input to power two.",
        ),
        encoding="utf-8",
    )

    context.help_database.refresh(force=True)

    assert "Raises the input" in (
        context.help_database.get("squareNumber").h1Line
    )


def test_function_help_database_can_be_used_without_context():
    database = FunctionHelpDatabase()

    assert database.get("sqrt").isBuiltin is True
