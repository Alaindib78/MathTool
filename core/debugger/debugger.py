class Debugger:
    def __init__(self):
        self.breakpoints = set()

        self.stepping = False

        self.paused = False

        self.current_node = None

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

    # ---------------------------------
    # Execution Hooks
    # ---------------------------------

    def before_node(self, node):
        line = getattr(node, "line", None)

        should_pause = False

        if (
            line is not None
            and self.has_breakpoint(line)
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
                pass

    # ---------------------------------
    # Controls
    # ---------------------------------

    def continue_execution(self):
        self.stepping = False

        self.paused = False

    def step(self):
        self.stepping = True

        self.paused = False