import numpy as np

from core.runtime.struct import MatlabStruct


class OptimizationResult(MatlabStruct):
    """Struct-like result for MATLAB-style optimization solvers."""

    def __init__(
        self,
        x,
        fval,
        exitflag,
        output,
        lambda_result=None,
        grad=None,
        hessian=None,
    ):
        super().__init__()
        self["x"] = x
        self["fval"] = fval
        self["exitflag"] = exitflag
        self["output"] = MatlabStruct(output)
        self["lambda"] = MatlabStruct(
            lambda_result or empty_lambda()
        )
        self["grad"] = (
            np.asarray(grad, dtype=float)
            if grad is not None
            else np.array([])
        )
        self["hessian"] = (
            np.asarray(hessian, dtype=float)
            if hessian is not None
            else np.array([])
        )

    @property
    def x(self):
        return self["x"]

    @property
    def fval(self):
        return self["fval"]

    @property
    def exitflag(self):
        return self["exitflag"]

    @property
    def output(self):
        return self["output"]


def empty_lambda():
    return {
        "lower": np.array([]),
        "upper": np.array([]),
        "ineqlin": np.array([]),
        "eqlin": np.array([]),
        "ineqnonlin": np.array([]),
        "eqnonlin": np.array([]),
    }
