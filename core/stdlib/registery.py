class FunctionRegistry:
    def __init__(self):
        self.functions = {}

    def register(self, name, func):
        self.functions[name] = func

    def get(self, name):
        if name not in self.functions:
            raise Exception(
                f"Undefined function '{name}'"
            )

        return self.functions[name]

    def exists(self, name):
        return name in self.functions