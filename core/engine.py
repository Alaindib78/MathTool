from dataclasses import dataclass, field

from core.interpreter.interpreter import Interpreter
from core.lexer.lexer import Lexer
from core.parser.parser import Parser
from core.runtime.context import RuntimeContext
from core.runtime.script_command import load_script_command
from core.semantic.semantic_analyzer import SemanticAnalyzer


_DEFAULT_OUTPUT_CALLBACK = object()


@dataclass
class ExecutionResult:
    value: object = None
    output: list[str] = field(default_factory=list)
    source_path: str | None = None
    command: str | None = None
    help_topic: str | None = None
    workspace_changed: bool = True
    clear_output: bool = False
    should_exit: bool = False


class MathToolSession:
    def __init__(
        self,
        context=None,
        output_callback=None,
        plot_engine=None,
        debugger=None,
    ):
        self.context = context or RuntimeContext()

        if output_callback is not None:
            self.context.output_callback = output_callback

        if plot_engine is not None:
            self.context.plot_engine = plot_engine

        if debugger is not None:
            self.context.debugger = debugger

        self.interpreter = Interpreter(
            self.context
        )

        self.semantic = SemanticAnalyzer(
            function_exists=self.context.function_exists
        )

    def execute(
        self,
        source,
        *,
        source_path=None,
        output_callback=_DEFAULT_OUTPUT_CALLBACK,
        allow_commands=False,
        allow_script_commands=False,
    ):
        with self.output_routing(output_callback) as output:
            if allow_commands:
                command_result = self.execute_command(
                    source
                )

                if command_result is not None:
                    command_result.output = output
                    return command_result

            result = self.execute_program(
                source,
                source_path=source_path,
                allow_script_commands=allow_script_commands,
            )

            result.output = output
            return result

    def execute_program(
        self,
        source,
        *,
        source_path=None,
        allow_script_commands=False,
    ):
        self.context.validate_function_paths()

        if allow_script_commands:
            script_command = load_script_command(
                self.context,
                source,
            )

            if script_command is not None:
                self.semantic.analyze(
                    script_command.ast
                )

                value = self.interpreter.evaluate(
                    script_command.ast,
                    source_path=script_command.path,
                )

                return ExecutionResult(
                    value=value,
                    source_path=script_command.path,
                )

        program = self.parse(source)

        self.semantic.analyze(program)

        value = self.interpreter.evaluate(
            program,
            source_path=source_path,
        )

        return ExecutionResult(
            value=value,
            source_path=source_path,
        )

    def parse(self, source):
        tokens = Lexer(source).tokenize()

        return Parser(tokens).parse()

    def execute_command(self, source):
        command = source.strip()
        lowered = command.lower()

        if lowered in (
            "exit",
            "quit",
        ):
            return ExecutionResult(
                command=lowered,
                workspace_changed=False,
                should_exit=True,
            )

        if lowered == "clear":
            self.context.clear()

            return ExecutionResult(
                value="Workspace cleared",
                command=lowered,
                workspace_changed=True,
            )

        if lowered == "clc":
            return ExecutionResult(
                command=lowered,
                workspace_changed=False,
                clear_output=True,
            )

        if lowered == "format" or lowered.startswith("format "):
            argument = self.command_argument(
                command,
                "format",
            )

            styles = (
                []
                if lowered == "format"
                else argument.split()
            )

            self.context.display_format.apply(*styles)

            return ExecutionResult(
                command="format",
                workspace_changed=True,
            )

        if lowered == "cwd":
            return ExecutionResult(
                value=self.context.current_working_directory,
                command=lowered,
                workspace_changed=False,
            )

        if lowered == "who":
            return ExecutionResult(
                value=self.context.who(),
                command=lowered,
                workspace_changed=False,
            )

        if lowered == "help":
            return ExecutionResult(
                value=self.context.help_database.format_help(),
                command=lowered,
                help_topic=None,
                workspace_changed=False,
            )

        if lowered.startswith("help "):
            topic = self.command_argument(command, "help")

            return ExecutionResult(
                value=self.context.help_database.format_help(
                    topic
                ),
                command="help",
                help_topic=topic,
                workspace_changed=False,
            )

        if lowered == "doc":
            return ExecutionResult(
                value=self.context.help_database.format_help(),
                command=lowered,
                help_topic=None,
                workspace_changed=False,
            )

        if lowered.startswith("doc "):
            topic = self.command_argument(command, "doc")

            return ExecutionResult(
                value=self.context.help_database.format_help(
                    topic
                ),
                command="doc",
                help_topic=topic,
                workspace_changed=False,
            )

        if lowered.startswith("lookfor "):
            keyword = self.command_argument(command, "lookfor")

            return ExecutionResult(
                value=self.context.help_database.format_lookfor(
                    keyword
                ),
                command="lookfor",
                workspace_changed=False,
            )

        return None

    def command_argument(self, command, name):
        argument = command[len(name):].strip()

        if argument.endswith(";"):
            argument = argument[:-1].strip()

        if (
            len(argument) >= 2
            and argument[0] == argument[-1]
            and argument[0] in {"'", '"'}
        ):
            argument = argument[1:-1]

        return argument

    def output_routing(self, output_callback):
        return OutputRouting(
            self.context,
            output_callback,
        )


class OutputRouting:
    def __init__(
        self,
        context,
        output_callback,
    ):
        self.context = context
        self.output_callback = output_callback
        self.output = []
        self.previous_callback = None

    def __enter__(self):
        self.previous_callback = (
            self.context.output_callback
        )

        if self.output_callback is _DEFAULT_OUTPUT_CALLBACK:
            active_callback = self.previous_callback
        else:
            active_callback = self.output_callback

        def route(text):
            self.output.append(text)

            if active_callback is not None:
                active_callback(text)

        self.context.output_callback = route

        return self.output

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        self.context.output_callback = (
            self.previous_callback
        )

        return False
