from core.stdlib.registery import FunctionRegistry
from core.stdlib.builtins import BUILTIN_FUNCTIONS
from core.plotting.engine import PlotEngine
from core.runtime.call_stack import CallStack
import math

class RuntimeContext:
    def __init__(self):
        self.variables = {}

        self.functions = FunctionRegistry()

        self.plot_engine = PlotEngine()

        self.call_stack = CallStack()

        for name, func in BUILTIN_FUNCTIONS.items():
            self.functions.register(name, func)

        self.variables["pi"] = math.pi
        self.variables["e"] = math.e
        self.variables["true"] = True
        self.variables["false"] = False

    def set_variable(self, name, value):
        self.variables[name] = value

    def get_variable(self, name):
        if name not in self.variables:
            raise Exception(
                f"Undefined variable '{name}'"
            )

        return self.variables[name]
    
    def create_child_context(self):
        child = RuntimeContext()

        child.functions = self.functions

        return child

    def clear(self):
        self.variables.clear()

    def who(self):
        return list(self.variables.keys())