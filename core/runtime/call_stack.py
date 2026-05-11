class CallFrame:
    def __init__(self, function_name):
        self.function_name = function_name

    def __repr__(self):
        return self.function_name


class CallStack:
    def __init__(self):
        self.frames = []

    def push(self, frame):
        self.frames.append(frame)

    def pop(self):
        if self.frames:
            self.frames.pop()

    def format_stack(self):
        if not self.frames:
            return ""

        lines = ["Call Stack:"]

        for frame in reversed(self.frames):
            lines.append(
                f"  at {frame.function_name}()"
            )

        return "\n".join(lines)