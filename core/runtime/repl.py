from core.lexer.lexer import Lexer
from core.parser.parser import Parser
from core.interpreter.interpreter import Interpreter
from core.runtime.context import RuntimeContext


class REPL:
    def __init__(self):
        self.running = True

        self.context = RuntimeContext()

        self.interpreter = Interpreter(
            self.context
        )

    def read_input(self):
        lines = []

        first_line = input(">> ")
        lines.append(first_line)

        if first_line.strip().lower() in {"exit", "who", "clear"}:
            return first_line

        while True:
            current = lines[-1].rstrip()

            # Continue if line does not end with semicolon
            # and is not empty
            if current.endswith(";") or current == "":
                break

            next_line = input(".. ")
            lines.append(next_line)

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
                print(f"Error: {e}")

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

        result = self.interpreter.evaluate(ast)

        print(result)