class FunctionRegistry:
    def __init__(self):
        self.functions = {}

        self.builtin_names = set()

    def register_builtin(self, name, func):
        self.functions[name] = func

        self.builtin_names.add(name)

    def register(self, name, func):
        if self.is_builtin(name):
            raise Exception(
                f"Cannot redefine built-in function '{name}'"
            )

        self.functions[name] = func

    def get(self, name):
        if name not in self.functions:
            raise Exception(
                f"Undefined function '{name}'"
            )

        return self.functions[name]

    def exists(self, name):
        return name in self.functions

    def is_builtin(self, name):
        return name in self.builtin_names
