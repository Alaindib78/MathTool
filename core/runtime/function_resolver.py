from pathlib import Path

from core.ast.nodes import FunctionDeclarationNode
from core.errors.errors import RuntimeError
from core.lexer.lexer import Lexer
from core.parser.parser import Parser
from core.runtime.user_function import UserFunction
from core.stdlib.builtins import BUILTIN_FUNCTIONS


def top_level_function_declarations(program):
    return [
        statement
        for statement in getattr(program, "statements", [])
        if isinstance(statement, FunctionDeclarationNode)
    ]


def nested_function_declarations(declaration):
    declarations = []

    for statement in declaration.body:
        if isinstance(statement, FunctionDeclarationNode):
            declarations.append(statement)
            declarations.extend(
                nested_function_declarations(statement)
            )

    return declarations


def build_user_functions(
    context,
    declarations,
    source_path=None,
):
    functions = {}
    all_declarations = []

    for declaration in declarations:
        all_declarations.append(declaration)
        all_declarations.extend(
            nested_function_declarations(declaration)
        )

    for declaration in all_declarations:
        if declaration.name in BUILTIN_FUNCTIONS:
            raise RuntimeError(
                f"Cannot redefine built-in function "
                f"'{declaration.name}'"
            )

        if declaration.name in functions:
            raise RuntimeError(
                f"Duplicate function definition "
                f"'{declaration.name}'"
            )

        functions[declaration.name] = UserFunction(
            declaration,
            context,
            source_path,
        )

    for function in functions.values():
        function.local_functions = functions

    return {
        declaration.name: functions[declaration.name]
        for declaration in declarations
    }


class FileFunctionResolver:
    def __init__(self, context):
        self.context = context

        self.file_cache = {}

    def invalidate(self):
        self.file_cache.clear()

    def exists(self, name):
        return self.resolve(name) is not None

    def resolve(self, name):
        if name in BUILTIN_FUNCTIONS:
            return None

        for directory in self.directories():
            direct_path = directory / f"{name}.m"

            if direct_path.is_file():
                return self.load_named_function(
                    name,
                    direct_path,
                )

            scanned_function = self.scan_directory(
                directory,
                name,
            )

            if scanned_function is not None:
                return scanned_function

        return None

    def validate_no_builtin_conflicts(self):
        for directory in self.directories():
            for path in self.m_files(directory):
                try:
                    program = self.parse_file(path)
                except Exception:
                    continue

                for declaration in (
                    top_level_function_declarations(program)
                ):
                    if declaration.name in BUILTIN_FUNCTIONS:
                        raise RuntimeError(
                            f"Function '{declaration.name}' "
                            f"in '{path}' conflicts with a "
                            f"built-in function"
                        )

    def directories(self):
        for _, directory in self.directory_entries():
            yield directory

    def directory_entries(self):
        directories = []

        current_directory = (
            self.context.current_working_directory
        )

        if current_directory:
            directories.append(
                ("Current working directory", current_directory)
            )

        for index, directory in enumerate(
            self.context.search_paths,
            start=1,
        ):
            directories.append(
                (f"External path #{index}", directory)
            )

        seen = set()

        for label, directory in directories:
            path = Path(directory).expanduser()

            try:
                resolved = path.resolve()
            except OSError:
                continue

            key = str(resolved)

            if key in seen or not resolved.is_dir():
                continue

            seen.add(key)

            yield label, resolved

    def function_locations(self):
        locations = {}

        for label, directory in self.directory_entries():
            for path in self.m_files(directory):
                try:
                    program = self.parse_file(path)
                except Exception:
                    continue

                for declaration in (
                    top_level_function_declarations(program)
                ):
                    locations.setdefault(
                        declaration.name,
                        [],
                    ).append(
                        {
                            "scope": label,
                            "directory": str(directory),
                            "path": str(path),
                        }
                    )

        return locations

    def scan_directory(self, directory, name):
        for path in self.m_files(directory):
            if path.stem == name:
                continue

            try:
                functions = self.load_file_functions(
                    path
                )
            except Exception:
                continue

            if name in functions:
                return functions[name]

        return None

    def load_named_function(self, name, path):
        functions = self.load_file_functions(path)

        if name in functions:
            return functions[name]

        if functions:
            raise RuntimeError(
                f"Function file '{path}' does not define "
                f"function '{name}'"
            )

        raise RuntimeError(
            f"Function file '{path}' does not contain a "
            f"valid function definition"
        )

    def load_file_functions(self, path):
        path = Path(path).resolve()
        cache_key = str(path)
        modified_time = path.stat().st_mtime_ns
        cached = self.file_cache.get(cache_key)

        if cached and cached[0] == modified_time:
            return cached[1]

        program = self.parse_file(path)

        declarations = top_level_function_declarations(
            program
        )

        functions = build_user_functions(
            self.context,
            declarations,
            str(path),
        )

        self.file_cache[cache_key] = (
            modified_time,
            functions,
        )

        return functions

    def parse_file(self, path):
        source = Path(path).read_text(
            encoding="utf-8"
        )

        tokens = Lexer(source).tokenize()

        return Parser(tokens).parse()

    def m_files(self, directory):
        return sorted(
            Path(directory).glob("*.m"),
            key=lambda path: path.name.lower(),
        )
