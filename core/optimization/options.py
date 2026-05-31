from dataclasses import dataclass
from math import isfinite

from core.errors.errors import RuntimeError as MathToolRuntimeError
from core.runtime.struct import MatlabStruct, is_struct


@dataclass
class OptimizationOptions:
    algorithm: str = "sqp"
    display: str = "off"
    max_iterations: int = 400
    max_function_evaluations: int = 10000
    step_tolerance: float = 1e-10
    optimality_tolerance: float = 1e-6
    constraint_tolerance: float = 1e-6
    function_tolerance: float = 1e-9
    finite_difference_type: str = "2-point"
    finite_difference_step_size: float = 1e-6
    specify_objective_gradient: bool = False
    specify_constraint_gradient: bool = False
    check_gradients: bool = False
    use_parallel: bool = False
    full_output: bool = False
    return_all: bool = False
    plot_iterations: bool = False


OPTION_FIELDS = {
    "algorithm": "algorithm",
    "display": "display",
    "maxiterations": "max_iterations",
    "maxiter": "max_iterations",
    "maxfunctionevaluations": "max_function_evaluations",
    "maxfunevals": "max_function_evaluations",
    "steptolerance": "step_tolerance",
    "tolfun": "function_tolerance",
    "functiontolerance": "function_tolerance",
    "optimalitytolerance": "optimality_tolerance",
    "constrainttolerance": "constraint_tolerance",
    "finitedifferencetype": "finite_difference_type",
    "finitedifferencestepsize": "finite_difference_step_size",
    "specifyobjectivegradient": "specify_objective_gradient",
    "specifyconstraintgradient": "specify_constraint_gradient",
    "checkgradients": "check_gradients",
    "useparallel": "use_parallel",
    "fulloutput": "full_output",
    "returnall": "return_all",
    "plotiterations": "plot_iterations",
}

SUPPORTED_ALGORITHMS = {
    "sqp",
    "sqp-legacy",
    "active-set",
    "interior-point",
    "trust-region-reflective",
}


def optimoptions(*arguments):
    if not arguments:
        raise MathToolRuntimeError(
            "optimoptions: expected solver name or options object"
        )

    first = arguments[0]
    if isinstance(first, OptimizationOptions):
        options = OptimizationOptions(**first.__dict__)
        remaining = arguments[1:]
    elif is_struct(first) and "algorithm" in lower_keys(first):
        options = options_from_struct(first)
        remaining = arguments[1:]
    else:
        solver = str(first).lower()
        if solver != "fmincon":
            raise MathToolRuntimeError(
                "optimoptions: only 'fmincon' is currently supported"
            )
        options = OptimizationOptions()
        remaining = arguments[1:]

    apply_name_value_options("optimoptions", options, remaining)
    validate_options("optimoptions", options)
    return options_to_struct(options)


def parse_optimization_options(function_name, arguments):
    options = OptimizationOptions()

    if not arguments:
        validate_options(function_name, options)
        return options

    first = arguments[0]
    if isinstance(first, OptimizationOptions):
        options = OptimizationOptions(**first.__dict__)
        remaining = arguments[1:]
    elif is_options_struct(first):
        options = options_from_struct(first)
        remaining = arguments[1:]
    else:
        remaining = arguments

    apply_name_value_options(function_name, options, remaining)
    validate_options(function_name, options)
    return options


def apply_name_value_options(function_name, options, arguments):
    index = 0
    while index < len(arguments):
        argument = arguments[index]

        if hasattr(argument, "name") and hasattr(argument, "value"):
            set_option(function_name, options, argument.name, argument.value)
            index += 1
            continue

        if not isinstance(argument, str):
            raise MathToolRuntimeError(
                f"{function_name}: expected Name,Value options"
            )

        if index + 1 >= len(arguments):
            raise MathToolRuntimeError(
                f"{function_name}: missing value for option '{argument}'"
            )

        set_option(function_name, options, argument, arguments[index + 1])
        index += 2


def set_option(function_name, options, name, value):
    key = normalize_key(name)
    if key not in OPTION_FIELDS:
        raise MathToolRuntimeError(
            f"{function_name}: unknown option '{name}'"
        )

    field_name = OPTION_FIELDS[key]
    setattr(
        options,
        field_name,
        coerce_option_value(function_name, name, field_name, value),
    )


def coerce_option_value(function_name, name, field_name, value):
    if field_name in {
        "algorithm",
        "display",
        "finite_difference_type",
    }:
        return str(value).lower()

    if field_name in {
        "max_iterations",
        "max_function_evaluations",
    }:
        try:
            return int(value)
        except (TypeError, ValueError) as error:
            raise MathToolRuntimeError(
                f"{function_name}: {name} must be an integer"
            ) from error

    if field_name in {
        "step_tolerance",
        "optimality_tolerance",
        "constraint_tolerance",
        "function_tolerance",
        "finite_difference_step_size",
    }:
        try:
            return float(value)
        except (TypeError, ValueError) as error:
            raise MathToolRuntimeError(
                f"{function_name}: {name} must be numeric"
            ) from error

    return option_bool(function_name, name, value)


def validate_options(function_name, options):
    if options.algorithm not in SUPPORTED_ALGORITHMS:
        raise MathToolRuntimeError(
            f"{function_name}: invalid Algorithm '{options.algorithm}'"
        )

    if options.display not in {"off", "iter", "final", "notify"}:
        raise MathToolRuntimeError(
            f"{function_name}: Display must be off, iter, final, or notify"
        )

    if options.finite_difference_type not in {"2-point", "3-point"}:
        raise MathToolRuntimeError(
            f"{function_name}: FiniteDifferenceType must be 2-point or 3-point"
        )

    if options.max_iterations <= 0:
        raise MathToolRuntimeError(
            f"{function_name}: MaxIterations must be positive"
        )

    if options.max_function_evaluations <= 0:
        raise MathToolRuntimeError(
            f"{function_name}: MaxFunctionEvaluations must be positive"
        )

    for field_name, label in [
        ("step_tolerance", "StepTolerance"),
        ("optimality_tolerance", "OptimalityTolerance"),
        ("constraint_tolerance", "ConstraintTolerance"),
        ("function_tolerance", "FunctionTolerance"),
        ("finite_difference_step_size", "FiniteDifferenceStepSize"),
    ]:
        value = getattr(options, field_name)
        if not isfinite(value) or value <= 0:
            raise MathToolRuntimeError(
                f"{function_name}: {label} must be positive"
            )


def options_from_struct(value):
    options = OptimizationOptions()
    for key, option_value in value.items():
        if normalize_key(key) in {
            "solver",
        }:
            continue
        set_option("fmincon", options, key, option_value)
    validate_options("fmincon", options)
    return options


def options_to_struct(options):
    result = MatlabStruct()
    result["Algorithm"] = options.algorithm
    result["Display"] = options.display
    result["MaxIterations"] = options.max_iterations
    result["MaxFunctionEvaluations"] = options.max_function_evaluations
    result["StepTolerance"] = options.step_tolerance
    result["OptimalityTolerance"] = options.optimality_tolerance
    result["ConstraintTolerance"] = options.constraint_tolerance
    result["FunctionTolerance"] = options.function_tolerance
    result["FiniteDifferenceType"] = options.finite_difference_type
    result["FiniteDifferenceStepSize"] = options.finite_difference_step_size
    result["SpecifyObjectiveGradient"] = options.specify_objective_gradient
    result["SpecifyConstraintGradient"] = options.specify_constraint_gradient
    result["CheckGradients"] = options.check_gradients
    result["UseParallel"] = options.use_parallel
    result["FullOutput"] = options.full_output
    result["ReturnAll"] = options.return_all
    result["PlotIterations"] = options.plot_iterations
    return result


def is_options_struct(value):
    return is_struct(value) and any(
        normalize_key(key) in OPTION_FIELDS
        for key in value
    )


def lower_keys(value):
    return {normalize_key(key) for key in value}


def normalize_key(name):
    return str(name).replace("_", "").replace(" ", "").lower()


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
