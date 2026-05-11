class SymbolTable:
    def __init__(self, parent=None):
        self.parent = parent

        self.symbols = {}

    def define(self, name, value=True):
        self.symbols[name] = value

    def exists_local(self, name):
        return name in self.symbols

    def exists(self, name):
        if name in self.symbols:
            return True

        if self.parent:
            return self.parent.exists(name)

        return False