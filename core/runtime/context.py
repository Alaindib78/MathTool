import os

from scipy import constants
from pathlib import Path

from core.stdlib.registery import FunctionRegistry
from core.stdlib.builtins import BUILTIN_FUNCTIONS
from core.plotting.engine import PlotEngine
from core.runtime.call_stack import CallStack
from core.runtime.function_resolver import FileFunctionResolver
from core.documentation.database import FunctionHelpDatabase
import math

RESERVED_CONSTANTS = {
    "pi",
    "e",
    "true",
    "false",
}

DEFAULT_IMAGINARY_UNITS = {
    "i": 1j,
    "j": 1j,
}

DEFAULT_LIBRARY_DIRECTORY = (
    Path(__file__).resolve().parent.parent
    / "library"
)


class RuntimeContext:
    def __init__(self):
        self.variables = {}

        self.functions = FunctionRegistry()

        self.plot_engine = PlotEngine()

        self.call_stack = CallStack()

        for name, func in BUILTIN_FUNCTIONS.items():
            self.functions.register_builtin(name, func)

        self.current_working_directory = str(
            Path.cwd()
        )

        self.search_paths = []

        self.library_paths = self.default_library_paths()

        self.function_resolver = FileFunctionResolver(
            self
        )

        self.help_database = FunctionHelpDatabase(
            self
        )

        self.file_function_stack = []

        self.current_source_path = None

        self.path_changed_callback = None

        self.load_constants()

        self.output_callback = None

        self.debugger = None

    def set_variable(self, name, value):
        self.variables[name] = value

    def get_variable(self, name):
        if name in DEFAULT_IMAGINARY_UNITS:
            return self.variables.get(
                name,
                DEFAULT_IMAGINARY_UNITS[name]
            )

        if name not in self.variables:
            raise Exception(
                f"Undefined variable '{name}'"
            )

        return self.variables[name]
    
    def create_child_context(self):
        child = RuntimeContext()

        child.functions = self.functions

        child.plot_engine = self.plot_engine

        child.call_stack = self.call_stack

        child.output_callback = self.output_callback

        child.debugger = self.debugger

        child.current_working_directory = (
            self.current_working_directory
        )

        child.search_paths = self.search_paths

        child.library_paths = self.library_paths

        child.function_resolver = self.function_resolver

        child.help_database = self.help_database

        child.file_function_stack = self.file_function_stack

        child.current_source_path = self.current_source_path

        child.path_changed_callback = (
            self.path_changed_callback
        )

        return child

    def set_current_working_directory(self, path):
        directory = self.normalize_directory(path)

        self.current_working_directory = directory

        self.function_resolver.invalidate()

        self.notify_path_changed()

    def set_search_paths(self, paths):
        self.search_paths = []

        for path in paths:
            self.add_search_path(path)

        self.function_resolver.invalidate()

        self.notify_path_changed()

    def add_search_path(self, path):
        directory = self.normalize_directory(path)

        if directory not in self.search_paths:
            self.search_paths.append(directory)

            self.function_resolver.invalidate()

            self.notify_path_changed()

    def default_library_paths(self):
        if not DEFAULT_LIBRARY_DIRECTORY.is_dir():
            return []

        directories = [
            DEFAULT_LIBRARY_DIRECTORY,
            *(
                path
                for path in DEFAULT_LIBRARY_DIRECTORY.rglob("*")
                if path.is_dir()
            ),
        ]

        return [
            str(path.resolve())
            for path in directories
        ]

    def remove_search_path(self, path):
        try:
            directory = self.normalize_directory(path)
        except ValueError:
            directory = str(path)

        if directory in self.search_paths:
            self.search_paths.remove(directory)

            self.function_resolver.invalidate()

            self.notify_path_changed()

    def normalize_directory(self, path):
        directory = Path(path).expanduser().resolve()

        if not directory.is_dir():
            raise ValueError(
                f"Directory does not exist: {path}"
            )

        if not os.access(directory, os.R_OK):
            raise ValueError(
                f"Directory is not accessible: {path}"
            )

        return str(directory)

    def notify_path_changed(self):
        if self.path_changed_callback is not None:
            self.path_changed_callback()

    def function_exists(self, name):
        if self.functions.is_builtin(name):
            return True

        if self.get_same_file_function(name) is not None:
            return True

        if self.function_resolver.exists(name):
            return True

        return self.functions.exists(name)

    def resolve_function(self, name):
        if self.functions.is_builtin(name):
            return self.functions.get(name)

        same_file_function = self.get_same_file_function(
            name
        )

        if same_file_function is not None:
            return same_file_function

        resolved_function = self.function_resolver.resolve(
            name
        )

        if resolved_function is not None:
            return resolved_function

        if self.functions.exists(name):
            return self.functions.get(name)

        return None

    def push_file_functions(self, functions):
        self.file_function_stack.append(functions)

    def pop_file_functions(self):
        self.file_function_stack.pop()

    def get_same_file_function(self, name):
        for functions in reversed(
            self.file_function_stack
        ):
            if name in functions:
                return functions[name]

        return None

    def validate_function_paths(self):
        self.function_resolver.validate_no_builtin_conflicts()

    def clear(self):
        constants = {
            key: value
            for key, value in self.variables.items()
            if key in RESERVED_CONSTANTS
        }

        self.variables.clear()

        self.variables.update(constants)

    def who(self):
        return [
            name
            for name in self.variables.keys()
            if name not in RESERVED_CONSTANTS
        ]
    
    def load_constants(self):
 
        self.variables["pi"] = math.pi
        self.variables["e"] = math.e
        self.variables["true"] = True
        self.variables["false"] = False
