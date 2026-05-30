from core.runtime.struct import MatlabStruct


class RootResult(MatlabStruct):
    """Struct-like scalar root solver result."""

    def __init__(self, root, fval, exitflag, output):
        super().__init__()
        self["root"] = root
        self["fval"] = fval
        self["exitflag"] = exitflag
        self["output"] = MatlabStruct(output)

    @property
    def root(self):
        return self["root"]

    @property
    def fval(self):
        return self["fval"]

    @property
    def exitflag(self):
        return self["exitflag"]

    @property
    def output(self):
        return self["output"]

    def as_outputs(self, count):
        values = [
            self.root,
            self.fval,
            self.exitflag,
            self.output,
        ]
        return tuple(values[:count])
