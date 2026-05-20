from pathlib import Path

from core.engine import MathToolSession
from core.runtime.formatting import format_value
from core.runtime.script_command import (
    script_command_name,
)


class REPL:
    def __init__(self):
        self.running = True

        self.session = MathToolSession()

        self.context = self.session.context

    def read_input(self):
        lines = []

        block_depth = 0

        first_line = input(">> ")
        first_line_command = first_line.strip().lower()

        if (
            first_line_command in {
                "exit",
                "who",
                "clear",
                "help",
                "cwd",
            }
            or first_line_command.startswith("help ")
            or first_line_command.startswith("lookfor ")
        ):
            return first_line

        if self.is_script_command(first_line):
            return first_line

        lines.append(first_line)

        if self.starts_block(first_line):
            block_depth += 1

        if self.ends_block(first_line):
            block_depth -= 1

        while True:
            current = lines[-1].rstrip()

            if block_depth <= 0 and (
                current.endswith(";")
                or current == ""
            ):
                break

            next_line = input(".. ")
            lines.append(next_line)

            if self.starts_block(next_line):
                block_depth += 1

            if self.ends_block(next_line):
                block_depth -= 1

        return "\n".join(lines)

    def start(self):
        print("MathTool REPL")
        print("Type 'exit' to quit.\n")

        while self.running:
            try:
                line = self.read_input()

                if line.strip() == "":
                    continue

                if line.strip().lower() == "exit":
                    self.running = False
                    continue

                self.execute(line)

            except KeyboardInterrupt:
                print("\nKeyboardInterrupt")

            except EOFError:
                print("\nExiting...")
                break

            except Exception as e:
                if getattr(
                    e,
                    "already_reported",
                    False,
                ):
                    continue

                print()

                print(e)

                if hasattr(
                    self.context,
                    "call_stack"
                ):
                    stack = (
                        self.context
                        .call_stack
                        .format_stack()
                    )

                    if stack:
                        print()
                        print(stack)

                print()


    def starts_block(self, line):
        stripped = line.strip()

        return (
            stripped.startswith("if ")
            or stripped.startswith("for ")
            or stripped.startswith("while ")
            or stripped.startswith("function ")
        )

    def ends_block(self, line):
        return line.strip() == "end"

    def execute(self, source):
        result = self.session.execute(
            source,
            allow_commands=True,
            allow_script_commands=True,
        )

        if result.should_exit:
            self.running = False
            return

        for text in result.output:
            print(text, end="")

        if result.value is not None:
            print(format_value(result.value))

    def is_script_command(self, source):
        name = script_command_name(source)

        if name is None:
            return False

        if name in self.context.variables:
            return False

        return (
            Path(self.context.current_working_directory)
            / f"{name}.m"
        ).is_file()
