from PySide6.QtCore import (
    QObject,
    Signal,
)

from threading import Event

from core.engine import MathToolSession


class ExecutionWorker(QObject):
    finished = Signal(object)

    error = Signal(str)

    output = Signal(str)

    input_requested = Signal(str)

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

        self.input_event = None

        self.input_response = ""

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
                    input_callback=self.request_input,
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

        if self.input_event is not None:
            self.input_response = ""
            self.input_event.set()

    def request_input(self, prompt):
        self.input_event = Event()
        self.input_response = ""

        self.input_requested.emit(prompt)

        self.input_event.wait()

        return self.input_response

    def submit_input_response(self, response):
        self.input_response = response

        if self.input_event is not None:
            self.input_event.set()
