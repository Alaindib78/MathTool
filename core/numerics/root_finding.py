import math

import numpy as np

from core.calculus.function_handle import FunctionHandle
from core.errors.errors import RuntimeError as MathToolRuntimeError
from core.numerics.root_result import RootResult
from core.numerics.solver_options import parse_root_solver_options


FZERO_DEFAULTS = {
    "tol_x": 1e-12,
    "max_iter": 100,
}
FZERO_OPTIONS = {
    "tolx",
    "maxiter",
    "display",
    "funvalcheck",
    "returnall",
    "fulloutput",
    "plotiterations",
}

NEWTON_DEFAULTS = {
    "tol_x": 1e-12,
    "tol_fun": 1e-12,
    "max_iter": 200,
    "damping": 1.0,
    "derivative_zero_tolerance": 1e-14,
}
NEWTON_OPTIONS = {
    "tolx",
    "tolfun",
    "maxiter",
    "display",
    "funvalcheck",
    "returnall",
    "fulloutput",
    "plotiterations",
    "damping",
    "derivativezerotolerance",
}

SECANT_DEFAULTS = {
    "tol_x": 1e-12,
    "tol_fun": 1e-12,
    "max_iter": 100,
    "denominator_tolerance": 1e-14,
}
SECANT_OPTIONS = {
    "tolx",
    "tolfun",
    "maxiter",
    "display",
    "funvalcheck",
    "returnall",
    "fulloutput",
    "plotiterations",
    "denominatortolerance",
}


def fzero_solver(fun, x0, *arguments, output_callback=None):
    options = parse_root_solver_options(
        "fzero",
        arguments,
        FZERO_DEFAULTS,
        FZERO_OPTIONS,
    )
    require_callable(fun, "fzero")

    trace = SolverTrace()
    display_header(
        output_callback,
        options,
        "Iter    x              f(x)             Procedure",
    )

    bracket = bracket_from_initial_value(
        fun,
        x0,
        options,
        trace,
    )

    if isinstance(bracket, RootResult):
        display_fzero_trace(output_callback, options, trace)
        return finish_result("fzero", bracket, options, output_callback)

    a, b, fa, fb = bracket

    result = brent_solve(fun, a, b, fa, fb, options, trace)
    display_fzero_trace(output_callback, options, trace)
    return finish_result("fzero", result, options, output_callback)


def newton_solver(fun, derivative, x0, *arguments, output_callback=None):
    options = parse_root_solver_options(
        "newtons_method",
        arguments,
        NEWTON_DEFAULTS,
        NEWTON_OPTIONS,
    )
    require_callable(fun, "newtons_method")
    require_callable(derivative, "newtons_method: derivative")

    x = numeric_scalar(x0, "newtons_method: x0")
    all_x = [x]
    fx = call_scalar_function(fun, x, "newtons_method", options)
    all_f = [fx]
    func_count = 1
    derivative_count = 0

    display_header(
        output_callback,
        options,
        "Iter    x              f(x)             df(x)            step",
    )

    for iteration in range(options.max_iter):
        dfx = call_scalar_function(
            derivative,
            x,
            "newtons_method: derivative",
            options,
        )
        derivative_count += 1

        if abs(dfx) < options.derivative_zero_tolerance:
            result = make_result(
                x,
                fx,
                -7,
                "Newton-Raphson",
                iteration,
                func_count,
                "newtons_method: derivative is zero or too small",
                all_x,
                all_f,
                derivativeCount=derivative_count,
            )
            return finish_result(
                "newtons_method",
                result,
                options,
                output_callback,
            )

        step = -options.damping * fx / dfx
        display_row(
            output_callback,
            options,
            f"{iteration:<7}{x:<15.8g}{fx:<16.8g}{dfx:<16.8g}{step:<15.8g}",
        )

        x_next = x + step
        if not math.isfinite(x_next):
            result = make_result(
                x,
                fx,
                -3,
                "Newton-Raphson",
                iteration,
                func_count,
                "newtons_method: non-finite iterate encountered",
                all_x,
                all_f,
                derivativeCount=derivative_count,
            )
            return finish_result(
                "newtons_method",
                result,
                options,
                output_callback,
            )

        fx_next = call_scalar_function(
            fun,
            x_next,
            "newtons_method",
            options,
        )
        func_count += 1
        all_x.append(x_next)
        all_f.append(fx_next)

        if abs(x_next - x) <= options.tol_x or abs(fx_next) <= options.tol_fun:
            result = make_result(
                x_next,
                fx_next,
                1,
                "Newton-Raphson",
                iteration + 1,
                func_count,
                "newtons_method converged",
                all_x,
                all_f,
                derivativeCount=derivative_count,
            )
            return finish_result(
                "newtons_method",
                result,
                options,
                output_callback,
            )

        if abs(step) > 1e12 * max(1.0, abs(x)):
            result = make_result(
                x_next,
                fx_next,
                -5,
                "Newton-Raphson",
                iteration + 1,
                func_count,
                "newtons_method: possible divergence or stagnation",
                all_x,
                all_f,
                derivativeCount=derivative_count,
            )
            return finish_result(
                "newtons_method",
                result,
                options,
                output_callback,
            )

        x, fx = x_next, fx_next

    result = make_result(
        x,
        fx,
        0,
        "Newton-Raphson",
        options.max_iter,
        func_count,
        "newtons_method: maximum iterations reached",
        all_x,
        all_f,
        derivativeCount=derivative_count,
    )
    return finish_result("newtons_method", result, options, output_callback)


def secant_solver(fun, x0, x1, *arguments, output_callback=None):
    options = parse_root_solver_options(
        "secant",
        arguments,
        SECANT_DEFAULTS,
        SECANT_OPTIONS,
    )
    require_callable(fun, "secant")

    x_prev = numeric_scalar(x0, "secant: x0")
    x = numeric_scalar(x1, "secant: x1")
    f_prev = call_scalar_function(fun, x_prev, "secant", options)
    fx = call_scalar_function(fun, x, "secant", options)
    func_count = 2
    all_x = [x_prev, x]
    all_f = [f_prev, fx]

    display_header(
        output_callback,
        options,
        "Iter    x              f(x)             step",
    )
    display_row(
        output_callback,
        options,
        f"{0:<7}{x_prev:<15.8g}{f_prev:<16.8g}{'initial':<15}",
    )
    display_row(
        output_callback,
        options,
        f"{1:<7}{x:<15.8g}{fx:<16.8g}{'initial':<15}",
    )

    if abs(f_prev) <= options.tol_fun:
        result = make_result(
            x_prev,
            f_prev,
            1,
            "Secant",
            0,
            func_count,
            "secant converged",
            all_x,
            all_f,
        )
        return finish_result("secant", result, options, output_callback)

    if abs(fx) <= options.tol_fun:
        result = make_result(
            x,
            fx,
            1,
            "Secant",
            0,
            func_count,
            "secant converged",
            all_x,
            all_f,
        )
        return finish_result("secant", result, options, output_callback)

    for iteration in range(1, options.max_iter + 1):
        denominator = fx - f_prev
        if abs(denominator) < options.denominator_tolerance:
            result = make_result(
                x,
                fx,
                -8,
                "Secant",
                iteration,
                func_count,
                "secant: denominator f(x1)-f(x0) is too small",
                all_x,
                all_f,
            )
            return finish_result("secant", result, options, output_callback)

        step = -fx * (x - x_prev) / denominator
        x_next = x + step
        if not math.isfinite(x_next):
            result = make_result(
                x,
                fx,
                -3,
                "Secant",
                iteration,
                func_count,
                "secant: non-finite iterate encountered",
                all_x,
                all_f,
            )
            return finish_result("secant", result, options, output_callback)

        f_next = call_scalar_function(fun, x_next, "secant", options)
        func_count += 1
        all_x.append(x_next)
        all_f.append(f_next)

        display_row(
            output_callback,
            options,
            f"{iteration + 1:<7}{x_next:<15.8g}{f_next:<16.8g}{step:<15.8g}",
        )

        if abs(x_next - x) <= options.tol_x or abs(f_next) <= options.tol_fun:
            result = make_result(
                x_next,
                f_next,
                1,
                "Secant",
                iteration,
                func_count,
                "secant converged",
                all_x,
                all_f,
            )
            return finish_result("secant", result, options, output_callback)

        x_prev, f_prev = x, fx
        x, fx = x_next, f_next

    result = make_result(
        x,
        fx,
        0,
        "Secant",
        options.max_iter,
        func_count,
        "secant: maximum iterations reached",
        all_x,
        all_f,
    )
    return finish_result("secant", result, options, output_callback)


def bracket_from_initial_value(fun, x0, options, trace):
    array = np.asarray(x0)

    if array.ndim == 0:
        start = numeric_scalar(x0, "fzero: x0")
        f_start = call_scalar_function(fun, start, "fzero", options)
        trace.add(start, f_start, "initial")

        if f_start == 0:
            return make_result(
                start,
                f_start,
                1,
                "Brent",
                0,
                1,
                "fzero converged at initial point",
                trace.all_x,
                trace.all_f,
                bracket=[start, start],
            )

        return find_bracket(fun, start, f_start, options, trace)

    flat = array.reshape(-1)
    if flat.size != 2:
        raise MathToolRuntimeError(
            "fzero: x0 must be a scalar or two-element interval"
        )

    a = numeric_scalar(flat[0], "fzero: x0(1)")
    b = numeric_scalar(flat[1], "fzero: x0(2)")

    if a == b:
        raise MathToolRuntimeError(
            "fzero: x0 interval endpoints must be distinct"
        )
    if a > b:
        a, b = b, a

    fa = call_scalar_function(fun, a, "fzero", options)
    fb = call_scalar_function(fun, b, "fzero", options)
    trace.add(a, fa, "initial")
    trace.add(b, fb, "initial")

    if fa == 0:
        return make_result(
            a,
            fa,
            1,
            "Brent",
            0,
            2,
            "fzero converged at interval endpoint",
            trace.all_x,
            trace.all_f,
            bracket=[a, b],
        )
    if fb == 0:
        return make_result(
            b,
            fb,
            1,
            "Brent",
            0,
            2,
            "fzero converged at interval endpoint",
            trace.all_x,
            trace.all_f,
            bracket=[a, b],
        )

    if not has_sign_change(fa, fb):
        result = make_result(
            a,
            fa,
            -6,
            "Brent",
            0,
            2,
            "fzero: x0 interval must contain a sign change",
            trace.all_x,
            trace.all_f,
            bracket=[a, b],
        )
        return result

    return a, b, fa, fb


def find_bracket(fun, start, f_start, options, trace):
    step = max(0.01, 0.025 * max(1.0, abs(start)))
    func_count = 1

    for iteration in range(1, 60):
        left = start - step
        right = start + step
        f_left = call_scalar_function(fun, left, "fzero", options)
        f_right = call_scalar_function(fun, right, "fzero", options)
        func_count += 2
        trace.add(left, f_left, "bracket-search")
        trace.add(right, f_right, "bracket-search")

        if f_left == 0:
            return make_result(
                left,
                f_left,
                1,
                "Brent",
                iteration,
                func_count,
                "fzero converged during bracket search",
                trace.all_x,
                trace.all_f,
                bracket=[left, left],
            )
        if f_right == 0:
            return make_result(
                right,
                f_right,
                1,
                "Brent",
                iteration,
                func_count,
                "fzero converged during bracket search",
                trace.all_x,
                trace.all_f,
                bracket=[right, right],
            )
        if has_sign_change(f_start, f_right):
            return start, right, f_start, f_right
        if has_sign_change(f_left, f_start):
            return left, start, f_left, f_start
        if has_sign_change(f_left, f_right):
            return left, right, f_left, f_right

        step *= 1.6

    return make_result(
        start,
        f_start,
        -6,
        "Brent",
        59,
        func_count,
        "fzero: could not find a sign-changing interval",
        trace.all_x,
        trace.all_f,
        bracket=[],
    )


def brent_solve(fun, a, b, fa, fb, options, trace):
    try:
        from scipy import optimize
    except ImportError:
        return fallback_bracket_solve(fun, a, b, fa, fb, options, trace)

    def wrapped(x):
        fx = call_scalar_function(fun, x, "fzero", options)
        trace.add(x, fx, "brent")
        return fx

    try:
        root, scipy_result = optimize.brentq(
            wrapped,
            a,
            b,
            xtol=options.tol_x,
            rtol=max(4.0 * np.finfo(float).eps, options.tol_x * 1e-3),
            maxiter=options.max_iter,
            full_output=True,
        )
    except ValueError as error:
        return make_result(
            a,
            fa,
            -6,
            "Brent",
            0,
            len(trace.all_x),
            f"fzero: {error}",
            trace.all_x,
            trace.all_f,
            bracket=[a, b],
        )

    fval = call_scalar_function(fun, root, "fzero", options)
    trace.add(root, fval, "final")

    exitflag = 1 if scipy_result.converged else 0
    message = (
        "fzero converged"
        if scipy_result.converged
        else "fzero: maximum iterations reached"
    )

    return make_result(
        root,
        fval,
        exitflag,
        "Brent",
        scipy_result.iterations,
        len(trace.all_x),
        message,
        trace.all_x,
        trace.all_f,
        bracket=[a, b],
    )


def fallback_bracket_solve(fun, a, b, fa, fb, options, trace):
    func_count = len(trace.all_x)
    left, right = a, b
    f_left, f_right = fa, fb
    root = left
    fval = f_left

    for iteration in range(1, options.max_iter + 1):
        if f_right != f_left:
            candidate = right - f_right * (right - left) / (f_right - f_left)
        else:
            candidate = (left + right) / 2.0

        if candidate <= left or candidate >= right:
            candidate = (left + right) / 2.0

        f_candidate = call_scalar_function(fun, candidate, "fzero", options)
        func_count += 1
        trace.add(candidate, f_candidate, "interpolation")
        root, fval = candidate, f_candidate

        if abs(f_candidate) <= options.tol_x or abs(right - left) <= options.tol_x:
            return make_result(
                root,
                fval,
                1,
                "Bisection/Secant",
                iteration,
                func_count,
                "fzero converged",
                trace.all_x,
                trace.all_f,
                bracket=[a, b],
            )

        if has_sign_change(f_left, f_candidate):
            right, f_right = candidate, f_candidate
        else:
            left, f_left = candidate, f_candidate

    return make_result(
        root,
        fval,
        0,
        "Bisection/Secant",
        options.max_iter,
        func_count,
        "fzero: maximum iterations reached",
        trace.all_x,
        trace.all_f,
        bracket=[a, b],
    )


def require_callable(value, function_name):
    if not isinstance(value, FunctionHandle) and not callable(value):
        raise MathToolRuntimeError(
            f"{function_name}: first argument must be a function handle"
        )


def call_scalar_function(fun, x, function_name, options):
    try:
        value = fun(float(x))
    except MathToolRuntimeError:
        raise
    except Exception as error:
        raise MathToolRuntimeError(
            f"{function_name}: error evaluating function: {error}"
        ) from error

    return validate_scalar_function_value(
        value,
        f"{function_name}: function value",
        options,
    )


def validate_scalar_function_value(value, label, options):
    if isinstance(value, np.generic):
        value = value.item()

    if isinstance(value, complex):
        if value.imag != 0:
            raise MathToolRuntimeError(
                f"{label} must be real scalar"
            )
        value = value.real

    array = np.asarray(value)
    if array.ndim != 0:
        raise MathToolRuntimeError(
            f"{label} must be real scalar"
        )

    try:
        scalar = array.item()
        if isinstance(scalar, complex):
            if scalar.imag != 0:
                raise MathToolRuntimeError(
                    f"{label} must be real scalar"
                )
            scalar = scalar.real
        scalar = float(scalar)
    except (TypeError, ValueError) as error:
        raise MathToolRuntimeError(
            f"{label} must be real scalar"
        ) from error

    if not math.isfinite(scalar):
        raise MathToolRuntimeError(
            f"{label} must be finite"
        )

    return scalar


def numeric_scalar(value, label):
    array = np.asarray(value)
    if array.ndim != 0:
        raise MathToolRuntimeError(
            f"{label} must be numeric scalar"
        )

    try:
        scalar = float(array.item())
    except (TypeError, ValueError) as error:
        raise MathToolRuntimeError(
            f"{label} must be numeric scalar"
        ) from error

    if not math.isfinite(scalar):
        raise MathToolRuntimeError(
            f"{label} must be finite"
        )

    return scalar


def has_sign_change(left, right):
    return (left < 0 < right) or (right < 0 < left)


def make_result(
    root,
    fval,
    exitflag,
    algorithm,
    iterations,
    func_count,
    message,
    all_x,
    all_f,
    **extra,
):
    output = {
        "iterations": iterations,
        "funcCount": func_count,
        "algorithm": algorithm,
        "message": message,
        "all_x": np.asarray(all_x, dtype=float),
        "all_f": np.asarray(all_f, dtype=float),
    }
    output.update(extra)
    return RootResult(root, fval, exitflag, output)


def finish_result(function_name, result, options, output_callback):
    if options.display == "final" or (
        options.display == "notify" and result.exitflag != 1
    ):
        write_output(output_callback, result.output["message"])

    if result.exitflag != 1 and not options.full_output:
        raise MathToolRuntimeError(result.output["message"])

    if options.full_output:
        return result

    return result.root


def display_header(output_callback, options, header):
    if options.display == "iter":
        write_output(output_callback, header)


def display_row(output_callback, options, row):
    if options.display == "iter":
        write_output(output_callback, row)


def display_fzero_trace(output_callback, options, trace):
    if options.display != "iter":
        return

    for index, (x, fx, procedure) in enumerate(
        zip(trace.all_x, trace.all_f, trace.procedures)
    ):
        write_output(
            output_callback,
            f"{index:<7}{x:<15.8g}{fx:<16.8g}{procedure:<15}",
        )


def write_output(output_callback, text):
    if output_callback is not None:
        output_callback(str(text) + "\n")


class SolverTrace:
    def __init__(self):
        self.all_x = []
        self.all_f = []
        self.procedures = []

    def add(self, x, fx, procedure):
        self.all_x.append(float(x))
        self.all_f.append(float(fx))
        self.procedures.append(procedure)
