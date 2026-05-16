from PySide6.QtCore import (
    QThread
)

class Debugger:
    def __init__(self):
        self.breakpoints = set()

        self.enabled = False

        self.stepping = False

        self.paused = False

        self.current_node = None

        self.resume_line = None

        self.pause_callback = None

    # ---------------------------------
    # Breakpoints
    # ---------------------------------

    def add_breakpoint(self, line):
        self.breakpoints.add(line)

    def remove_breakpoint(self, line):
        self.breakpoints.discard(line)

    def has_breakpoint(self, line):
        return line in self.breakpoints

    def set_breakpoints(self, lines):
        self.breakpoints = {
            int(line)
            for line in lines
            if int(line) > 0
        }

    def clear_breakpoints(self):
        self.breakpoints.clear()

    # ---------------------------------
    # Execution Hooks
    # ---------------------------------

    def before_node(self, node):
        if not self.enabled:
            return

        line = getattr(node, "line", None)

        if line is None:
            return

        if self.resume_line == line:
            return

        self.resume_line = None

        should_pause = False

        if (
            self.has_breakpoint(line)
        ):
            should_pause = True

        if self.stepping:
            should_pause = True

        if should_pause:
            self.paused = True

            self.current_node = node

            if self.pause_callback:
                self.pause_callback(node)


            while self.paused:
                QThread.msleep(10)

    # ---------------------------------
    # Controls
    # ---------------------------------

    def start_session(self):
        self.enabled = True

        self.stepping = False

        self.paused = False

        self.current_node = None

        self.resume_line = None

    def stop_session(self):
        self.enabled = False

        self.stepping = False

        self.paused = False

        self.current_node = None

        self.resume_line = None

    def continue_execution(self):
        if self.current_node is not None:
            self.resume_line = getattr(
                self.current_node,
                "line",
                None,
            )

        self.stepping = False

        self.paused = False

    def step(self):
        if self.current_node is not None:
            self.resume_line = getattr(
                self.current_node,
                "line",
                None,
            )

        self.enabled = True

        self.stepping = True

        self.paused = False
