from PySide6.QtCore import (
    QObject,
    Signal,
)

from core.engine import MathToolSession


class ExecutionWorker(QObject):
    finished = Signal(object)

    error = Signal(str)

    output = Signal(str)

    workspace_updated = Signal()

    def __init__(
        self,
        source,
        session_or_semantic,
        interpreter=None,
        source_path=None,
    ):
        super().__init__()

        self.source = source

        if isinstance(
            session_or_semantic,
            MathToolSession,
        ):
            self.session = session_or_semantic
        else:
            self.session = MathToolSession(
                context=interpreter.context
            )

            self.session.semantic = session_or_semantic
            self.session.interpreter = interpreter

        self.source_path = source_path

        self.cancelled = False

    # ---------------------------------
    # Execution
    # ---------------------------------

    def run(self):
        if self.cancelled:
            self.finished.emit(None)
            return

        try:
            result = (
                self.session.execute(
                    self.source,
                    source_path=self.source_path,
                    output_callback=self.output.emit,
                    allow_commands=False,
                    allow_script_commands=False,
                )
            )

            self.workspace_updated.emit()
            self.finished.emit(result.value)

        except Exception as e:
            if getattr(e, "already_reported", False):
                self.error.emit("")
            else:
                self.error.emit(str(e))

    # ---------------------------------
    # Cancellation
    # ---------------------------------

    def cancel(self):
        self.cancelled = True
