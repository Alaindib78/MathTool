from scipy import constants

from core.stdlib.registery import FunctionRegistry
from core.stdlib.builtins import BUILTIN_FUNCTIONS
from core.plotting.engine import PlotEngine
from core.runtime.call_stack import CallStack
import math

RESERVED_CONSTANTS = {
    "pi",
    "e",
    "true",
    "false",
}

DEFAULT_IMAGINARY_UNITS = {
    "i": 1j,
    "j": 1j,
}

class RuntimeContext:
    def __init__(self):
        self.variables = {}

        self.functions = FunctionRegistry()

        self.plot_engine = PlotEngine()

        self.call_stack = CallStack()

        for name, func in BUILTIN_FUNCTIONS.items():
            self.functions.register(name, func)

        self.load_constants()

        self.output_callback = None

        self.debugger = None

    def set_variable(self, name, value):
        self.variables[name] = value

    def get_variable(self, name):
        if name in DEFAULT_IMAGINARY_UNITS:
            return self.variables.get(
                name,
                DEFAULT_IMAGINARY_UNITS[name]
            )

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
        constants = {
            key: value
            for key, value in self.variables.items()
            if key in RESERVED_CONSTANTS
        }

        self.variables.clear()

        self.variables.update(constants)

    def who(self):
        return [
            name
            for name in self.variables.keys()
            if name not in RESERVED_CONSTANTS
        ]
    
    def load_constants(self):
 
        self.variables["pi"] = math.pi
        self.variables["e"] = math.e
        self.variables["true"] = True
        self.variables["false"] = False
