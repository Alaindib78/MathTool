import math

import numpy as np

from core.calculus.function_handle import FunctionHandle
from core.errors.errors import RuntimeError as MathToolRuntimeError
from core.optimization.finite_difference import finite_difference_gradient
from core.optimization.optimization_result import OptimizationResult
from core.optimization.options import (
    is_options_struct,
    parse_optimization_options,
)
from core.runtime.struct import MatlabStruct, is_struct


def fmincon_solver(*arguments, output_callback=None, plot_engine=None):
    problem = parse_fmincon_arguments(arguments)
    options = problem["options"]
    require_callable(problem["fun"], "fmincon")

    try:
        from scipy import optimize
    except ImportError as error:
        raise MathToolRuntimeError(
            "fmincon: scipy is required"
        ) from error

    x0, original_shape = numeric_initial_point(problem["x0"])
    n_variables = x0.size
    linear_ineq = linear_constraint(
        problem["A"],
        problem["b"],
        n_variables,
        "fmincon: A",
        "fmincon: b",
    )
    linear_eq = linear_constraint(
        problem["Aeq"],
        problem["beq"],
        n_variables,
        "fmincon: Aeq",
        "fmincon: beq",
    )
    lower, upper = build_bounds(problem["lb"], problem["ub"], n_variables)
    projected_x0 = project_into_bounds(x0, lower, upper)

    if not np.allclose(projected_x0, x0) and options.display in {"iter", "final"}:
        write_output(
            output_callback,
            "fmincon: initial point was projected into bounds",
        )

    history = OptimizationHistory()

    def shaped(vector):
        return shape_vector(vector, original_shape)

    def objective_flat(vector):
        return evaluate_objective(problem["fun"], shaped(vector))

    constraints = build_scipy_constraints(
        problem["nonlcon"],
        linear_ineq,
        linear_eq,
        shaped,
        options,
    )

    display_header(output_callback, options)

    def callback(vector):
        fval = objective_flat(vector)
        violation = constraint_violation(
            vector,
            linear_ineq,
            linear_eq,
            lower,
            upper,
            problem["nonlcon"],
            shaped,
        )
        step = history.step_norm(vector)
        history.add(vector, fval, violation, step)
        display_iteration(output_callback, options, history)

    method = scipy_method(options.algorithm)

    try:
        scipy_result = optimize.minimize(
            objective_flat,
            projected_x0,
            method=method,
            bounds=list(zip(lower, upper)),
            constraints=constraints,
            callback=callback,
            options={
                "maxiter": options.max_iterations,
                "ftol": options.function_tolerance,
                "disp": False,
            },
        )
    except MathToolRuntimeError:
        raise
    except Exception as error:
        raise MathToolRuntimeError(
            f"fmincon: solver failed: {error}"
        ) from error

    x_flat = np.asarray(scipy_result.x, dtype=float).reshape(-1)
    x_value = shaped(x_flat)
    fval = evaluate_objective(problem["fun"], x_value)
    violation = constraint_violation(
        x_flat,
        linear_ineq,
        linear_eq,
        lower,
        upper,
        problem["nonlcon"],
        shaped,
    )
    gradient = finite_difference_gradient(
        objective_flat,
        x_flat,
        options.finite_difference_step_size,
        options.finite_difference_type,
    )
    first_order = float(np.linalg.norm(gradient, ord=np.inf))
    exitflag = exitflag_from_scipy(
        scipy_result,
        violation,
        options.constraint_tolerance,
    )
    message = fmincon_message(scipy_result, exitflag, violation, options)

    output = MatlabStruct()
    output["iterations"] = int(getattr(scipy_result, "nit", len(history.all_x)))
    output["funcCount"] = int(getattr(scipy_result, "nfev", 0))
    output["algorithm"] = algorithm_label(options.algorithm)
    output["message"] = message
    output["constrviolation"] = violation
    output["firstorderopt"] = first_order
    output["stepsize"] = history.last_step()
    output["bestfeasible"] = x_value if violation <= options.constraint_tolerance else np.array([])
    output["all_x"] = np.asarray(history.all_x, dtype=float)
    output["all_f"] = np.asarray(history.all_f, dtype=float)
    output["success"] = bool(getattr(scipy_result, "success", False))
    output["scipy_status"] = int(getattr(scipy_result, "status", 0))
    output["scipy_message"] = str(getattr(scipy_result, "message", ""))

    result = OptimizationResult(
        x_value,
        fval,
        exitflag,
        output,
        lambda_result=lambda_result(n_variables, linear_ineq, linear_eq),
        grad=gradient,
    )

    display_final(output_callback, options, result)

    if options.full_output:
        return result

    if exitflag < 0:
        raise MathToolRuntimeError(message)

    return result.x


def parse_fmincon_arguments(arguments):
    if len(arguments) == 1 and is_struct(arguments[0]):
        return problem_from_struct(arguments[0])

    if len(arguments) < 2:
        raise MathToolRuntimeError(
            "fmincon expects fmincon(fun, x0, ...)"
        )

    fun = arguments[0]
    x0 = arguments[1]
    remaining = list(arguments[2:])

    option_start = first_option_index(remaining)
    positional = remaining[:option_start]
    option_arguments = remaining[option_start:]
    options = parse_optimization_options("fmincon", option_arguments)

    values = positional + [None] * (7 - len(positional))
    if len(values) > 7:
        raise MathToolRuntimeError(
            "fmincon: too many positional arguments"
        )

    A, b, Aeq, beq, lb, ub, nonlcon = values[:7]
    return {
        "fun": fun,
        "x0": x0,
        "A": empty_to_none(A),
        "b": empty_to_none(b),
        "Aeq": empty_to_none(Aeq),
        "beq": empty_to_none(beq),
        "lb": empty_to_none(lb),
        "ub": empty_to_none(ub),
        "nonlcon": empty_to_none(nonlcon),
        "options": options,
    }


def problem_from_struct(problem):
    solver = get_struct_field(problem, "solver")
    if solver is not None and str(solver).lower() != "fmincon":
        raise MathToolRuntimeError(
            "fmincon: problem.solver must be 'fmincon'"
        )

    objective = get_struct_field(problem, "objective")
    x0 = get_struct_field(problem, "x0")
    if objective is None or x0 is None:
        raise MathToolRuntimeError(
            "fmincon: problem objective and x0 are required"
        )

    options_value = get_struct_field(problem, "options")
    option_arguments = [options_value] if options_value is not None else []

    return {
        "fun": objective,
        "x0": x0,
        "A": empty_to_none(
            first_present(
                get_struct_field(problem, "Aineq"),
                get_struct_field(problem, "A"),
            )
        ),
        "b": empty_to_none(
            first_present(
                get_struct_field(problem, "bineq"),
                get_struct_field(problem, "b"),
            )
        ),
        "Aeq": empty_to_none(get_struct_field(problem, "Aeq")),
        "beq": empty_to_none(get_struct_field(problem, "beq")),
        "lb": empty_to_none(get_struct_field(problem, "lb")),
        "ub": empty_to_none(get_struct_field(problem, "ub")),
        "nonlcon": empty_to_none(get_struct_field(problem, "nonlcon")),
        "options": parse_optimization_options("fmincon", option_arguments),
    }


def first_present(*values):
    for value in values:
        if value is not None:
            return value
    return None


def first_option_index(arguments):
    for index, argument in enumerate(arguments):
        if hasattr(argument, "name") and hasattr(argument, "value"):
            return index
        if isinstance(argument, str):
            return index
        if is_options_struct(argument):
            return index
    return len(arguments)


def require_callable(value, function_name):
    if not isinstance(value, FunctionHandle) and not callable(value):
        raise MathToolRuntimeError(
            f"{function_name}: objective must be a function handle"
        )


def numeric_initial_point(value):
    try:
        array = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as error:
        raise MathToolRuntimeError(
            "fmincon: x0 must be numeric"
        ) from error

    if array.size == 0:
        raise MathToolRuntimeError(
            "fmincon: x0 must not be empty"
        )

    if not np.all(np.isfinite(array)):
        raise MathToolRuntimeError(
            "fmincon: x0 must be finite"
        )

    return array.reshape(-1), array.shape


def shape_vector(vector, shape):
    array = np.asarray(vector, dtype=float).reshape(shape)
    if array.ndim == 0:
        return float(array.item())
    return array


def evaluate_objective(fun, x):
    try:
        value = fun(x)
    except MathToolRuntimeError:
        raise
    except Exception as error:
        raise MathToolRuntimeError(
            f"fmincon: error evaluating objective: {error}"
        ) from error

    return scalar_value(
        value,
        "fmincon: objective function must return a real scalar",
    )


def scalar_value(value, message):
    if isinstance(value, np.generic):
        value = value.item()

    if isinstance(value, complex):
        if value.imag != 0:
            raise MathToolRuntimeError(message)
        value = value.real

    array = np.asarray(value)
    if array.ndim != 0:
        raise MathToolRuntimeError(message)

    try:
        scalar = array.item()
        if isinstance(scalar, complex):
            if scalar.imag != 0:
                raise MathToolRuntimeError(message)
            scalar = scalar.real
        scalar = float(scalar)
    except (TypeError, ValueError) as error:
        raise MathToolRuntimeError(message) from error

    if not math.isfinite(scalar):
        raise MathToolRuntimeError(message)

    return scalar


def vector_values(value, message):
    if value is None:
        return np.array([], dtype=float)

    array = np.asarray(value, dtype=float).reshape(-1)
    if array.size == 0:
        return array

    if np.iscomplexobj(array) or not np.all(np.isfinite(array)):
        raise MathToolRuntimeError(message)

    return array


def linear_constraint(A, b, n_variables, A_name, b_name):
    A = empty_to_none(A)
    b = empty_to_none(b)
    if A is None and b is None:
        return None

    if A is None or b is None:
        raise MathToolRuntimeError(
            f"{A_name} and {b_name} must be provided together"
        )

    try:
        matrix = np.asarray(A, dtype=float)
        vector = np.asarray(b, dtype=float).reshape(-1)
    except (TypeError, ValueError) as error:
        raise MathToolRuntimeError(
            f"{A_name} and {b_name} must be numeric"
        ) from error

    if matrix.ndim == 1:
        matrix = matrix.reshape(1, -1)

    if matrix.ndim != 2:
        raise MathToolRuntimeError(
            f"{A_name} must be a numeric matrix"
        )

    if matrix.shape[1] != n_variables:
        raise MathToolRuntimeError(
            f"{A_name} must have one column per optimization variable"
        )

    if matrix.shape[0] != vector.size:
        raise MathToolRuntimeError(
            f"{b_name} length must match rows of {A_name}"
        )

    return matrix, vector


def build_bounds(lb, ub, n_variables):
    lower = bound_vector(lb, n_variables, -np.inf, "fmincon: lb")
    upper = bound_vector(ub, n_variables, np.inf, "fmincon: ub")

    if np.any(lower > upper):
        raise MathToolRuntimeError(
            "fmincon: lower bound cannot exceed upper bound"
        )

    return lower, upper


def bound_vector(value, n_variables, default, label):
    value = empty_to_none(value)
    if value is None:
        return np.full(n_variables, default, dtype=float)

    try:
        array = np.asarray(value, dtype=float).reshape(-1)
    except (TypeError, ValueError) as error:
        raise MathToolRuntimeError(
            f"{label} must be numeric"
        ) from error

    if array.size == 1:
        array = np.full(n_variables, float(array[0]), dtype=float)
    elif array.size != n_variables:
        raise MathToolRuntimeError(
            f"{label} length must match number of variables"
        )

    return array


def project_into_bounds(x0, lower, upper):
    return np.minimum(np.maximum(x0, lower), upper)


def build_scipy_constraints(nonlcon, linear_ineq, linear_eq, shaped, options):
    constraints = []

    if linear_ineq is not None:
        matrix, vector = linear_ineq
        constraints.append(
            {
                "type": "ineq",
                "fun": lambda x, A=matrix, b=vector: b - A.dot(x),
            }
        )

    if linear_eq is not None:
        matrix, vector = linear_eq
        constraints.append(
            {
                "type": "eq",
                "fun": lambda x, A=matrix, b=vector: A.dot(x) - b,
            }
        )

    if nonlcon is not None:
        require_callable_nonlcon(nonlcon)
        constraints.append(
            {
                "type": "ineq",
                "fun": lambda x: -evaluate_nonlcon(nonlcon, shaped(x))[0],
            }
        )
        constraints.append(
            {
                "type": "eq",
                "fun": lambda x: evaluate_nonlcon(nonlcon, shaped(x))[1],
            }
        )

    return constraints


def require_callable_nonlcon(nonlcon):
    if not isinstance(nonlcon, FunctionHandle) and not callable(nonlcon):
        raise MathToolRuntimeError(
            "fmincon: nonlinear constraint must be a function handle"
        )


def evaluate_nonlcon(nonlcon, x):
    try:
        value = nonlcon(x)
    except MathToolRuntimeError:
        raise
    except Exception as error:
        raise MathToolRuntimeError(
            f"fmincon: error evaluating nonlinear constraints: {error}"
        ) from error

    if is_struct(value):
        c = get_struct_field(value, "c")
        ceq = get_struct_field(value, "ceq")
        return (
            vector_values(c, "fmincon: nonlinear constraints must be finite real values"),
            vector_values(ceq, "fmincon: nonlinear constraints must be finite real values"),
        )

    if isinstance(value, tuple):
        values = list(value)
    else:
        array = np.asarray(value, dtype=object)
        values = list(array.reshape(-1))

    if len(values) == 1:
        c = values[0]
        ceq = np.array([])
    elif len(values) == 2:
        c, ceq = values
    else:
        raise MathToolRuntimeError(
            "fmincon: nonlinear constraint function must return [c, ceq]"
        )

    return (
        vector_values(c, "fmincon: nonlinear constraints must be finite real values"),
        vector_values(ceq, "fmincon: nonlinear constraints must be finite real values"),
    )


def constraint_violation(
    x,
    linear_ineq,
    linear_eq,
    lower,
    upper,
    nonlcon,
    shaped,
):
    violations = [0.0]
    if linear_ineq is not None:
        matrix, vector = linear_ineq
        violations.append(max_positive(matrix.dot(x) - vector))

    if linear_eq is not None:
        matrix, vector = linear_eq
        violations.append(max_abs(matrix.dot(x) - vector))

    violations.append(max_positive(lower - x))
    violations.append(max_positive(x - upper))

    if nonlcon is not None:
        c, ceq = evaluate_nonlcon(nonlcon, shaped(x))
        violations.append(max_positive(c))
        violations.append(max_abs(ceq))

    return float(max(violations))


def max_positive(values):
    values = np.asarray(values, dtype=float).reshape(-1)
    if values.size == 0:
        return 0.0
    return float(max(0.0, np.max(values)))


def max_abs(values):
    values = np.asarray(values, dtype=float).reshape(-1)
    if values.size == 0:
        return 0.0
    return float(np.max(np.abs(values)))


def scipy_method(algorithm):
    return "SLSQP"


def algorithm_label(algorithm):
    if algorithm in {
        "active-set",
        "interior-point",
        "trust-region-reflective",
    }:
        return f"{algorithm} (SLSQP backend)"
    return "SLSQP"


def exitflag_from_scipy(result, violation, tolerance):
    status = int(getattr(result, "status", 0))
    success = bool(getattr(result, "success", False))

    if violation > tolerance:
        return -2
    if success:
        return 1
    if status in {8, 9}:
        return 0
    if status in {4, 6}:
        return -2
    return -5


def fmincon_message(result, exitflag, violation, options):
    if exitflag == 1:
        return "fmincon converged to a feasible solution"
    if exitflag == 0:
        return "fmincon: maximum iterations or function evaluations exceeded"
    if exitflag == -2:
        return (
            "fmincon: no feasible point found; "
            f"constraint violation is {violation:.3g}"
        )
    return f"fmincon: solver failed: {getattr(result, 'message', '')}"


def lambda_result(n_variables, linear_ineq, linear_eq):
    return {
        "lower": np.zeros(n_variables),
        "upper": np.zeros(n_variables),
        "ineqlin": (
            np.zeros(linear_ineq[1].size)
            if linear_ineq is not None
            else np.array([])
        ),
        "eqlin": (
            np.zeros(linear_eq[1].size)
            if linear_eq is not None
            else np.array([])
        ),
        "ineqnonlin": np.array([]),
        "eqnonlin": np.array([]),
    }


def display_header(output_callback, options):
    if options.display == "iter":
        write_output(
            output_callback,
            "Iter    Func-count    f(x)             Constraint     Step-size       Algorithm",
        )


def display_iteration(output_callback, options, history):
    if options.display != "iter":
        return

    index = len(history.all_x)
    write_output(
        output_callback,
        f"{index:<8}{history.func_count:<14}{history.all_f[-1]:<16.8g}"
        f"{history.violations[-1]:<15.8g}{history.steps[-1]:<16.8g}SLSQP",
    )


def display_final(output_callback, options, result):
    should_display = options.display == "final" or (
        options.display == "notify" and result.exitflag != 1
    )
    if should_display:
        write_output(output_callback, result.output["message"])


def write_output(output_callback, text):
    if output_callback is not None:
        output_callback(str(text) + "\n")


def get_struct_field(value, field_name):
    lowered = str(field_name).lower()
    for key, item in value.items():
        if str(key).lower() == lowered:
            return item
    return None


def empty_to_none(value):
    if value is None:
        return None
    try:
        array = np.asarray(value)
    except Exception:
        return value
    if array.size == 0:
        return None
    return value


class OptimizationHistory:
    def __init__(self):
        self.all_x = []
        self.all_f = []
        self.violations = []
        self.steps = []
        self.func_count = 0

    def add(self, x, fval, violation, step):
        self.all_x.append(np.asarray(x, dtype=float).copy())
        self.all_f.append(float(fval))
        self.violations.append(float(violation))
        self.steps.append(float(step))
        self.func_count += 1

    def step_norm(self, x):
        if not self.all_x:
            return 0.0
        return float(np.linalg.norm(np.asarray(x) - self.all_x[-1]))

    def last_step(self):
        if not self.steps:
            return 0.0
        return self.steps[-1]
