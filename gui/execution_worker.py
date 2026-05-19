from PySide6.QtCore import (
    QObject,
    Signal,
)

from core.lexer.lexer import Lexer
from core.parser.parser import Parser


class ExecutionWorker(QObject):
    finished = Signal(object)

    error = Signal(str)

    output = Signal(str)

    workspace_updated = Signal()

    def __init__(
        self,
        source,
        semantic,
        interpreter,
    ):
        super().__init__()

        self.source = source

        self.semantic = semantic

        self.interpreter = interpreter

        self.cancelled = False

    # ---------------------------------
    # Execution
    # ---------------------------------

    def run(self):
        original_output_callback = (
            self.interpreter.context.output_callback
        )

        self.interpreter.context.output_callback = (
            self.output.emit
        )

        try:
            lexer = Lexer(self.source)

            tokens = lexer.tokenize()

            parser = Parser(tokens)

            ast = parser.parse()

            self.semantic.analyze(ast)

            if self.cancelled:
                self.finished.emit(None)
                return

            result = (
                self.interpreter.evaluate(ast)
            )

            self.workspace_updated.emit()
            self.finished.emit(result)

        except Exception as e:
            if getattr(e, "already_reported", False):
                self.error.emit("")
            else:
                self.error.emit(str(e))

        finally:
            self.interpreter.context.output_callback = (
                original_output_callback
            )

    # ---------------------------------
    # Cancellation
    # ---------------------------------

    def cancel(self):
        self.cancelled = True
