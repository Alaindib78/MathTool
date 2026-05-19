from core.lexer.lexer import Lexer
from core.parser.parser import Parser
from core.interpreter.interpreter import Interpreter
from core.runtime.context import RuntimeContext
from core.runtime.formatting import format_value
from core.semantic.semantic_analyzer import SemanticAnalyzer


class REPL:
    def __init__(self):
        self.running = True

        self.context = RuntimeContext()

        self.interpreter = Interpreter(
            self.context
        )

        self.semantic_analyzer = (
            SemanticAnalyzer()
        )

#if first_line.strip().lower() in {"exit", "who", "clear"}:
#            return first_line

    def read_input(self):
        lines = []

        block_depth = 0

        first_line = input(">> ")
        first_line_command = first_line.strip().lower()

        if (
            first_line_command in {"exit", "who", "clear", "help"}
            or first_line_command.startswith("help ")
        ):
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
        if source.strip() == "who":
            print(self.context.who())
            return

        if source.strip() == "clear":
            self.context.clear()
            print("Workspace cleared")
            return

        lexer = Lexer(source)

        tokens = lexer.tokenize()

        parser = Parser(tokens)

        ast = parser.parse()

        self.semantic_analyzer.analyze(ast)

        result = self.interpreter.evaluate(ast)

        if result is not None:
            print(format_value(result))
