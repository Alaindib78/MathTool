import re
from dataclasses import dataclass
from pathlib import Path

from core.ast.nodes import FunctionDeclarationNode
from core.errors.errors import RuntimeError
from core.lexer.lexer import KEYWORDS, Lexer
from core.parser.parser import Parser


SCRIPT_COMMAND_PATTERN = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_]*;?$"
)


@dataclass(frozen=True)
class ScriptCommand:
    path: str
    source: str
    ast: object


def load_script_command(context, command):
    name = script_command_name(command)

    if name is None:
        return None

    if name in context.variables:
        return None

    directory = Path(
        context.current_working_directory
    )

    path = directory / f"{name}.m"

    try:
        if not path.is_file():
            return None

        path = path.resolve()

        source = path.read_text(
            encoding="utf-8"
        )
    except OSError as error:
        raise RuntimeError(
            f"Script file '{path}' is not accessible: "
            f"{error}"
        ) from error

    ast = Parser(Lexer(source).tokenize()).parse()

    if not is_script_program(ast):
        return None

    return ScriptCommand(
        path=str(path),
        source=source,
        ast=ast,
    )


def script_command_name(command):
    stripped = command.strip()

    if not SCRIPT_COMMAND_PATTERN.match(stripped):
        return None

    name = stripped.rstrip(";")

    if name in KEYWORDS:
        return None

    return name


def is_script_program(program):
    return any(
        not isinstance(
            statement,
            FunctionDeclarationNode,
        )
        for statement in getattr(
            program,
            "statements",
            [],
        )
    )
