from dataclasses import dataclass
from math import isfinite

from core.errors.errors import RuntimeError as MathToolRuntimeError
from core.runtime.struct import is_struct


@dataclass
class RootSolverOptions:
    tol_x: float = 1e-12
    tol_fun: float = 1e-12
    max_iter: int = 100
    display: str = "off"
    fun_val_check: bool = False
    return_all: bool = False
    full_output: bool = False
    plot_iterations: bool = False
    damping: float = 1.0
    derivative_zero_tolerance: float = 1e-14
    denominator_tolerance: float = 1e-14


OPTION_FIELDS = {
    "tolx": "tol_x",
    "tolfun": "tol_fun",
    "maxiter": "max_iter",
    "display": "display",
    "funvalcheck": "fun_val_check",
    "returnall": "return_all",
    "fulloutput": "full_output",
    "plotiterations": "plot_iterations",
    "damping": "damping",
    "derivativezerotolerance": "derivative_zero_tolerance",
    "denominatortolerance": "denominator_tolerance",
}


def parse_root_solver_options(function_name, arguments, defaults, allowed):
    options = RootSolverOptions(**defaults)
    pending = list(arguments)

    if pending and is_struct(pending[0]):
        struct_options = pending.pop(0)
        for key, value in struct_options.items():
            apply_option(function_name, options, key, value, allowed)

    index = 0
    while index < len(pending):
        argument = pending[index]

        if hasattr(argument, "name") and hasattr(argument, "value"):
            apply_option(
                function_name,
                options,
                argument.name,
                argument.value,
                allowed,
            )
            index += 1
            continue

        if not isinstance(argument, str):
            raise MathToolRuntimeError(
                f"{function_name}: expected Name,Value options"
            )

        if index + 1 >= len(pending):
            raise MathToolRuntimeError(
                f"{function_name}: missing value for option '{argument}'"
            )

        apply_option(
            function_name,
            options,
            argument,
            pending[index + 1],
            allowed,
        )
        index += 2

    validate_options(function_name, options, allowed)
    return options


def apply_option(function_name, options, name, value, allowed):
    key = str(name).lower()
    if key not in OPTION_FIELDS or key not in allowed:
        raise MathToolRuntimeError(
            f"{function_name}: unknown option '{name}'"
        )

    setattr(
        options,
        OPTION_FIELDS[key],
        coerce_option_value(function_name, name, value),
    )


def coerce_option_value(function_name, name, value):
    key = str(name).lower()

    if key in {
        "tolx",
        "tolfun",
        "damping",
        "derivativezerotolerance",
        "denominatortolerance",
    }:
        try:
            return float(value)
        except (TypeError, ValueError) as error:
            raise MathToolRuntimeError(
                f"{function_name}: {name} must be numeric"
            ) from error

    if key == "maxiter":
        try:
            return int(value)
        except (TypeError, ValueError) as error:
            raise MathToolRuntimeError(
                f"{function_name}: MaxIter must be an integer"
            ) from error

    if key == "display":
        return str(value).lower()

    if key == "funvalcheck":
        return on_off_bool(function_name, name, value)

    if key in {"returnall", "fulloutput", "plotiterations"}:
        return option_bool(function_name, name, value)

    return value


def validate_options(function_name, options, allowed):
    if options.display not in {"off", "iter", "final", "notify"}:
        raise MathToolRuntimeError(
            f"{function_name}: Display must be off, iter, final, or notify"
        )

    allowed_fields = [OPTION_FIELDS[key] for key in allowed]

    for field_name, label in [
        ("tol_x", "TolX"),
        ("tol_fun", "TolFun"),
        ("derivative_zero_tolerance", "DerivativeZeroTolerance"),
        ("denominator_tolerance", "DenominatorTolerance"),
    ]:
        if field_name not in allowed_fields:
            continue
        value = getattr(options, field_name)
        if not isfinite(value) or value <= 0:
            raise MathToolRuntimeError(
                f"{function_name}: {label} must be positive"
            )

    if options.max_iter <= 0:
        raise MathToolRuntimeError(
            f"{function_name}: MaxIter must be positive"
        )

    if "damping" in allowed_fields:
        if not isfinite(options.damping) or options.damping <= 0:
            raise MathToolRuntimeError(
                f"{function_name}: Damping must be positive"
            )


def option_bool(function_name, name, value):
    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return bool(value)

    if isinstance(value, str):
        lowered = value.lower()
        if lowered in {"true", "on", "yes", "1"}:
            return True
        if lowered in {"false", "off", "no", "0"}:
            return False

    raise MathToolRuntimeError(
        f"{function_name}: {name} must be true or false"
    )


def on_off_bool(function_name, name, value):
    if isinstance(value, str):
        lowered = value.lower()
        if lowered == "on":
            return True
        if lowered == "off":
            return False

    return option_bool(function_name, name, value)
