class Context:

    def __init__(self):

        self.variables = {}

    def set_variable(self, name, value):

        self.variables[name] = value

    def get_variable(self, name):

        if name not in self.variables:
            raise Exception(
                f"Undefined variable '{name}'"
            )

        return self.variables[name]

    def __repr__(self):

        return str(self.variables)