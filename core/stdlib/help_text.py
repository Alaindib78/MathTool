def entry(
    summary,
    signatures,
    inputs,
    output,
    options="None.",
    examples=None,
    see_also=None,
):
    if isinstance(signatures, str):
        signatures = [signatures]

    return {
        "summary": summary,
        "signatures": signatures,
        "inputs": inputs,
        "output": output,
        "options": options,
        "examples": examples or [],
        "see_also": see_also or [],
    }


HELP_TOPICS = {}
HELP_CATEGORIES = {}


def add(name, category, *args, **kwargs):
    HELP_TOPICS[name] = entry(*args, **kwargs)
    HELP_CATEGORIES.setdefault(category, []).append(name)


def add_unary(name, category, summary, output=None, examples=None):
    add(
        name,
        category,
        summary,
        f"{name}(x)",
        "x: scalar, vector, matrix, or array-like numeric input.",
        output or "Same shape as x, with the operation applied element-wise.",
        examples=examples,
    )


def add_reduction(name, summary, output):
    add(
        name,
        "reductions and statistics",
        summary,
        [f"{name}(A)", f"{name}(A, dim)"],
        (
            "A: numeric or logical scalar, vector, matrix, or array. "
            "dim: optional 1-based dimension to reduce along."
        ),
        output,
        "When dim is omitted, MathTool reduces all elements to a scalar.",
        [f"{name}([1 2; 3 4])", f"{name}([1 2; 3 4], 1)"],
    )


# Console and diagnostics
add(
    "disp",
    "console",
    "Display one value using readable MATLAB-style formatting.",
    "disp(value)",
    "value: string, number, logical, array, matrix, struct/dictionary, or empty value.",
    "Writes formatted text to the console and appends a newline. Returns no value.",
    "Newline is automatic.",
    ["disp('Hello')", "disp([1 2; 3 4])"],
)
add(
    "fprintf",
    "console",
    "Format and write text without adding an automatic newline.",
    "fprintf(formatString, arg1, ...)",
    "formatString: text containing %s, %d/%i, or %f placeholders. argN: values for placeholders.",
    "Writes the formatted text to the console. Returns no value.",
    "Supports C-style precision such as %.2f. Use \\n in the format string for a newline.",
    ["fprintf('x = %.2f\\n', 3.14159)"],
)
add(
    "warning",
    "console",
    "Display a non-fatal warning and continue execution.",
    "warning(message, arg1, ...)",
    "message: plain text or fprintf-style format string. argN: optional formatting values.",
    "Writes a message prefixed with 'Warning:'. Returns no value.",
    "Supports the same placeholders as fprintf.",
    ["warning('gain %.1f is high', 12.5)"],
)
add(
    "error",
    "console",
    "Display a fatal error and abort execution.",
    "error(message, arg1, ...)",
    "message: plain text or fprintf-style format string. argN: optional formatting values.",
    "Writes a message prefixed with 'Error:' and throws an exception.",
    "Supports the same placeholders as fprintf.",
    ["error('File %s not found', 'data.csv')"],
)
add(
    "help",
    "console",
    "Show documentation for a function or list available help topics.",
    ["help", "help functionName", "help('functionName')"],
    "functionName: optional builtin or user function name, supplied command-style or as a string.",
    "Returns explanatory text. In the GUI, it is written directly to the console.",
    "No options.",
    ["help eig", "help('linspace')"],
)
add(
    "lookfor",
    "console",
    "Search function H1 lines and descriptions.",
    ["lookfor keyword", "lookfor('keyword')"],
    "keyword: search text supplied command-style or as a string.",
    "Returns matching function names with short descriptions.",
    "Searches built-ins and documented functions on the current function path.",
    ["lookfor eigen", "lookfor('matrix')"],
    see_also=["help"],
)
add(
    "cwd",
    "console",
    "Return the active current working directory.",
    ["cwd", "cwd()"],
    "No inputs.",
    "Returns the current working directory used for script and function lookup.",
    "Matches the directory shown in the GUI current folder panel.",
    ["cwd", "disp(cwd())"],
)
add(
    "who",
    "console",
    "List variables in the current workspace.",
    ["who", "who()"],
    "No inputs.",
    "Returns a list of workspace variable names, excluding built-in constants.",
    "Matches the Workspace panel contents.",
    ["who"],
)


# Trigonometry and angles
for name, summary in {
    "sin": "Sine of an angle in radians.",
    "cos": "Cosine of an angle in radians.",
    "tan": "Tangent of an angle in radians.",
    "asin": "Inverse sine, returning radians.",
    "acos": "Inverse cosine, returning radians.",
    "atan": "Inverse tangent, returning radians.",
    "sinh": "Hyperbolic sine.",
    "cosh": "Hyperbolic cosine.",
    "tanh": "Hyperbolic tangent.",
    "asinh": "Inverse hyperbolic sine.",
    "acosh": "Inverse hyperbolic cosine.",
    "atanh": "Inverse hyperbolic tangent.",
}.items():
    add_unary(name, "trigonometry", summary)

add(
    "atan2",
    "trigonometry",
    "Four-quadrant inverse tangent of y/x, returning radians.",
    "atan2(y, x)",
    "y, x: scalars or compatible arrays.",
    "Angle(s) in radians, with shape broadcast from y and x.",
    "No options.",
    ["atan2(1, 1)"],
)
add_unary("deg2rad", "trigonometry", "Convert degrees to radians.")
add_unary("rad2deg", "trigonometry", "Convert radians to degrees.")


# Element-wise math and complex numbers
for name, summary in {
    "log": "Natural logarithm.",
    "log10": "Base-10 logarithm.",
    "log2": "Base-2 logarithm.",
    "exp": "Exponential e^x.",
    "expm1": "Compute exp(x) - 1 accurately for small x.",
    "sqrt": "Square root. Negative real inputs produce complex results.",
    "abs": "Absolute value or complex magnitude.",
    "floor": "Round each value toward negative infinity.",
    "ceil": "Round each value toward positive infinity.",
    "fix": "Round each value toward zero.",
    "sign": "Sign of each value.",
}.items():
    add_unary(name, "element-wise math", summary)

add(
    "round",
    "element-wise math",
    "Round values to the nearest integer or decimal place.",
    ["round(x)", "round(x, decimals)"],
    "x: numeric input. decimals: optional number of decimal places.",
    "Rounded scalar or array.",
    "decimals defaults to 0.",
    ["round(3.14159, 2)"],
)
add(
    "clip",
    "element-wise math",
    "Limit values to a lower and upper bound.",
    "clip(x, lower, upper)",
    "x: numeric input. lower, upper: scalar or compatible bounds.",
    "Values of x constrained to [lower, upper].",
    "No options.",
    ["clip([-2 0 5], 0, 3)"],
)
add(
    "complex",
    "complex numbers",
    "Construct complex numbers from real and optional imaginary parts.",
    ["complex(real)", "complex(real, imag)"],
    "real: numeric scalar/array. imag: optional imaginary component.",
    "Complex scalar or array.",
    "If imag is omitted, real is converted to complex type.",
    ["complex(3, -4)"],
)
for name, summary, output in [
    ("real", "Extract real component.", "Real component of z."),
    ("imag", "Extract imaginary component.", "Imaginary component of z."),
    ("angle", "Return phase angle of complex values.", "Phase angle(s) in radians."),
    ("conj", "Return complex conjugate.", "Conjugated scalar or array."),
]:
    add_unary(name, "complex numbers", summary, output)
add(
    "isreal",
    "complex numbers",
    "Test whether a value is stored as a real-valued object.",
    "isreal(value)",
    "value: scalar, array, or matrix.",
    "Logical true if value is not a complex object; otherwise false.",
    "No options.",
    ["isreal([1 2 3])"],
)


# Array construction and shape
for name, summary, signature, output, options in [
    ("zeros", "Create an array of zeros.", "zeros(m, n, ...)", "Array of zeros with requested shape.", "A single scalar creates an n-by-n matrix."),
    ("ones", "Create an array of ones.", "ones(m, n, ...)", "Array of ones with requested shape.", "A single scalar creates an n-by-n matrix."),
    ("true", "Create a logical array filled with true.", "true(m, n, ...)", "Logical array with requested shape.", "A single scalar creates an n-by-n matrix."),
    ("false", "Create a logical array filled with false.", "false(m, n, ...)", "Logical array with requested shape.", "A single scalar creates an n-by-n matrix."),
    ("zeros_like", "Create zeros with the same shape and type as another value.", "zeros_like(A)", "Array matching A's shape filled with zeros.", "No options."),
    ("ones_like", "Create ones with the same shape and type as another value.", "ones_like(A)", "Array matching A's shape filled with ones.", "No options."),
    ("eye", "Create an identity matrix.", "eye(n, m)", "Identity-like matrix with ones on the main diagonal.", "m is optional; eye(n) creates n-by-n."),
    ("reshape", "Reshape an array without changing its data.", "reshape(A, m, n, ...)", "Array A viewed with the requested shape.", "Element count must match."),
    ("transpose", "Transpose an array.", "transpose(A)", "Array with axes reversed; for matrices, rows and columns are swapped.", "No options."),
    ("flatten", "Flatten an array to a row vector.", "flatten(A)", "One-dimensional array containing all elements of A.", "No options."),
    ("diag", "Create a diagonal matrix or extract a diagonal.", "diag(A, k)", "If A is a vector, returns a diagonal matrix; if A is a matrix, returns a diagonal vector.", "k is optional diagonal offset."),
    ("tril", "Return the lower triangular part of a matrix.", "tril(A, k)", "Matrix with elements above the kth diagonal set to zero.", "k defaults to 0."),
    ("triu", "Return the upper triangular part of a matrix.", "triu(A, k)", "Matrix with elements below the kth diagonal set to zero.", "k defaults to 0."),
]:
    add(
        name,
        "array construction and shape",
        summary,
        signature,
        "A: scalar, vector, matrix, or array-like value as required. Dimensions are positive integers.",
        output,
        options,
        [signature],
    )

add(
    "linspace",
    "array construction and shape",
    "Create linearly spaced points over an interval.",
    "linspace(start, stop, num)",
    "start, stop: endpoints. num: optional number of samples.",
    "Vector of evenly spaced values including start and stop.",
    "num defaults to 100.",
    ["linspace(0, 1, 5)"],
)
add(
    "logspace",
    "array construction and shape",
    "Create logarithmically spaced powers of 10.",
    "logspace(start, stop, num)",
    "start, stop: exponents. num: optional number of samples.",
    "Vector from 10^start to 10^stop.",
    "num defaults to 50.",
    ["logspace(0, 3, 4)"],
)
add(
    "arange",
    "array construction and shape",
    "Create evenly spaced values using half-open interval semantics.",
    ["arange(stop)", "arange(start, stop, step)"],
    "start: first value. stop: exclusive limit. step: spacing.",
    "Vector of values [start, start+step, ...] before stop.",
    "If only one argument is supplied it is treated as stop.",
    ["arange(1, 6, 2)"],
)
for name, summary, output in [
    ("size", "Return array dimensions.", "Shape vector, or size along a requested dimension."),
    ("length", "Return largest array dimension length.", "Largest dimension size, or 1 for scalars."),
    ("numel", "Return number of elements.", "Integer element count."),
    ("ndims", "Return number of dimensions.", "Integer dimension count."),
    ("isempty", "Test whether an array has zero elements.", "Logical true for empty arrays."),
]:
    add(
        name,
        "array construction and shape",
        summary,
        [f"{name}(A)", f"{name}(A, dim)" if name == "size" else f"{name}(A)"],
        "A: scalar, vector, matrix, or array. dim: optional 1-based dimension for size only.",
        output,
        "Dimension arguments are 1-based.",
        [f"{name}([1 2; 3 4])"],
    )


# Random numbers
for name, summary, signature, output in [
    ("rand", "Uniform random samples on [0, 1).", "rand(m, n, ...)", "Random scalar or array."),
    ("randn", "Standard normal random samples.", "randn(m, n, ...)", "Random scalar or array."),
    ("randi", "Uniform random integers from 1 to high.", "randi(high, m, n, ...)", "Random integer scalar or array."),
]:
    add(
        name,
        "random numbers",
        summary,
        signature,
        "Dimensions are optional positive integers.",
        output,
        "A single dimension creates an n-by-n matrix for MATLAB-style convenience.",
        [signature],
    )
add(
    "rng",
    "random numbers",
    "Set or reset the random number generator seed.",
    ["rng(seed)", "rng()"],
    "seed: optional integer seed.",
    "Returns no value. Subsequent rand/randn/randi calls use the configured generator.",
    "Omit seed to create a fresh unpredictable generator.",
    ["rng(123)"],
)


# Reductions and statistics
for name, summary, output in [
    ("sum", "Sum elements.", "Sum as scalar or reduced array."),
    ("prod", "Multiply elements.", "Product as scalar or reduced array."),
    ("mean", "Average elements.", "Mean as scalar or reduced array."),
    ("median", "Median of elements.", "Median as scalar or reduced array."),
    ("max", "Maximum element.", "Maximum as scalar or reduced array."),
    ("min", "Minimum element.", "Minimum as scalar or reduced array."),
]:
    add_reduction(name, summary, output)

for name, summary in [
    ("std", "Standard deviation."),
    ("var", "Variance."),
]:
    add(
        name,
        "reductions and statistics",
        summary,
        [f"{name}(A)", f"{name}(A, dim)", f"{name}(A, dim, ddof)"],
        "A: numeric data. dim: optional 1-based dimension. ddof: optional delta degrees of freedom.",
        "Statistic as scalar or reduced array.",
        "ddof defaults to 0.",
        [f"{name}([1 2 3])"],
    )
add(
    "percentile",
    "reductions and statistics",
    "Percentile of data.",
    ["percentile(A, q)", "percentile(A, q, dim)"],
    "A: numeric data. q: percentile from 0 to 100. dim: optional 1-based dimension.",
    "Requested percentile as scalar or reduced array.",
    "No interpolation options are currently exposed.",
    ["percentile([1 2 3 4], 50)"],
)


# Logical tests, search, and ordering
for name, summary, output in [
    ("any", "Test whether any element is nonzero/true.", "Logical scalar or reduced logical array."),
    ("all", "Test whether all elements are nonzero/true.", "Logical scalar or reduced logical array."),
]:
    add(
        name,
        "logical tests and search",
        summary,
        [f"{name}(A)", f"{name}(A, dim)"],
        "A: numeric or logical data. dim: optional 1-based dimension.",
        output,
        "Without dim, all elements are tested.",
        [f"{name}([0 1])"],
    )
for name, summary in [
    ("isnan", "Test for NaN values."),
    ("isinf", "Test for infinite values."),
    ("isfinite", "Test for finite values."),
]:
    add_unary(
        name,
        "logical tests and search",
        summary,
        "Logical scalar or array with the same shape as input.",
    )
add(
    "isclose",
    "logical tests and search",
    "Element-wise approximate equality test.",
    "isclose(A, B, rtol, atol)",
    "A, B: scalars or compatible arrays. rtol, atol: optional relative and absolute tolerances.",
    "Logical scalar or array.",
    "rtol defaults to 1e-5; atol defaults to 1e-8.",
    ["isclose(1, 1 + 1e-9)"],
)
add(
    "allclose",
    "logical tests and search",
    "Approximate equality test over all elements.",
    "allclose(A, B, rtol, atol)",
    "A, B: scalars or compatible arrays. rtol, atol: optional tolerances.",
    "Logical scalar.",
    "rtol defaults to 1e-5; atol defaults to 1e-8.",
    ["allclose([1 2], [1 2.000000001])"],
)
for name, summary, output in [
    ("sort", "Sort array values.", "Sorted array."),
    ("unique", "Return sorted unique values.", "Vector of unique values."),
    ("find", "Find nonzero/true element positions.", "One-based linear indices."),
]:
    add(
        name,
        "logical tests and search",
        summary,
        [f"{name}(A)", f"{name}(A, dim)" if name == "sort" else f"{name}(A)"],
        "A: scalar, vector, matrix, or array. dim: optional 1-based sort dimension.",
        output,
        "sort uses the last axis by default.",
        [f"{name}([3 1 3])"],
    )


# Numerical calculus and signal helpers
for name, summary, signature, inputs, output, options, examples in [
    ("diff", "Discrete differences along an array dimension.", "diff(A, n, dim)", "A: numeric array. n: optional difference order. dim: optional 1-based dimension.", "Array of differences.", "n defaults to 1; dim defaults to the first non-singleton dimension.", ["diff([1 4 9])"]),
    ("gradient", "Numerical gradient estimate.", "gradient(A)", "A: numeric vector or matrix.", "Gradient array, or stacked gradient arrays for multi-dimensional input.", "Spacing options are not currently exposed.", ["gradient([1 4 9])"]),
    ("cumsum", "Cumulative sum.", "cumsum(A, dim)", "A: numeric array. dim: optional 1-based dimension.", "Array of cumulative sums.", "Without dim, uses flattened order.", ["cumsum([1 2 3])"]),
    ("cumprod", "Cumulative product.", "cumprod(A, dim)", "A: numeric array. dim: optional 1-based dimension.", "Array of cumulative products.", "Without dim, uses flattened order.", ["cumprod([1 2 3])"]),
    ("trapz", "Trapezoidal numerical integration.", "trapz(x, y)", "x: sample locations or y-values. y: optional y-values.", "Scalar integral estimate.", "If y is omitted, unit spacing is assumed.", ["trapz([0 1 2], [0 1 0])"]),
    ("interp1", "One-dimensional linear interpolation.", "interp1(x, y, query)", "x: sample locations. y: sample values. query: scalar or vector query points.", "Interpolated scalar or array.", "Extrapolation is not currently exposed.", ["interp1([0 1], [0 10], 0.5)"]),
    ("mod", "Remainder after division.", "mod(a, b)", "a, b: scalars or compatible arrays.", "Element-wise remainder.", "No options.", ["mod(7, 3)"]),
]:
    add(
        name,
        "numerical calculus and signal helpers",
        summary,
        signature,
        inputs,
        output,
        options,
        examples,
    )


# Linear algebra
for name, summary, signature, output, options in [
    ("det", "Matrix determinant.", "det(A)", "Scalar determinant.", "A must be square."),
    ("inv", "Matrix inverse.", "inv(A)", "Inverse matrix.", "A must be square and nonsingular."),
    ("pinv", "Moore-Penrose pseudoinverse.", "pinv(A)", "Pseudoinverse matrix.", "Useful for rectangular or rank-deficient systems."),
    ("linsolve", "Solve a linear system A*x = b.", "linsolve(A, b)", "Solution vector or matrix x.", "Raises an error for singular systems."),
    ("eig", "Eigenvalue decomposition of a square matrix.", "eig(A)", "Struct with fields values and vectors.", "A must be square. Eigenvectors are returned by columns."),
    ("svd", "Singular value decomposition.", "svd(A)", "Struct with fields U, S, and Vt.", "S is returned as a vector of singular values."),
    ("qr", "QR factorization.", "qr(A)", "Struct with fields Q and R.", "Uses NumPy's reduced QR convention."),
    ("dot", "Dot product or matrix product depending on input ranks.", "dot(A, B)", "Scalar or array dot product result.", "Inputs must have compatible shapes."),
    ("cross", "3D vector cross product.", "cross(A, B)", "Vector cross product.", "Inputs must be length-3 vectors or compatible arrays."),
    ("norm", "Vector or matrix norm.", "norm(A, order)", "Scalar norm.", "order is optional."),
    ("trace", "Sum of matrix diagonal.", "trace(A)", "Scalar trace.", "No options."),
    ("rank", "Matrix rank.", "rank(A)", "Integer matrix rank.", "Uses numerical rank estimation."),
    ("cond", "Matrix condition number.", "cond(A)", "Scalar condition number.", "Large values indicate ill conditioning."),
]:
    add(
        name,
        "linear algebra",
        summary,
        signature,
        "A, B: numeric vectors or matrices as required.",
        output,
        options,
        [signature],
    )


# FFT and polynomials
for name, summary, signature, output, options, examples in [
    ("fft", "Discrete Fourier transform.", "fft(x, n)", "Complex spectrum.", "n is optional transform length.", ["fft([1 0 0 0])"]),
    ("ifft", "Inverse discrete Fourier transform.", "ifft(x, n)", "Complex time-domain samples.", "n is optional transform length.", ["ifft(fft([1 0 0 0]))"]),
    ("fftshift", "Shift zero-frequency component to the center.", "fftshift(x)", "Shifted array.", "No options.", ["fftshift([-2 -1 0 1])"]),
    ("ifftshift", "Inverse of fftshift.", "ifftshift(x)", "Unshifted array.", "No options.", ["ifftshift(fftshift(x))"]),
    ("fftfreq", "Frequency bins for an FFT length.", "fftfreq(n, d)", "Vector of frequency bins.", "d is optional sample spacing and defaults to 1.", ["fftfreq(8, 0.1)"]),
    ("roots", "Polynomial roots.", "roots(coefficients)", "Vector of roots.", "Coefficients are ordered highest power first.", ["roots([1 0 -1])"]),
    ("polyval", "Evaluate a polynomial.", "polyval(coefficients, x)", "Scalar or array polynomial values.", "Coefficients are ordered highest power first.", ["polyval([1 0 -1], 3)"]),
    ("polyfit", "Least-squares polynomial fit.", "polyfit(x, y, degree)", "Coefficient vector ordered highest power first.", "degree is an integer polynomial degree.", ["polyfit([0 1 2], [1 2 5], 2)"]),
    ("conv", "One-dimensional discrete convolution.", "conv(a, b)", "Convolution vector.", "No options.", ["conv([1 2], [3 4])"]),
]:
    add(
        name,
        "FFT and polynomials",
        summary,
        signature,
        "Numeric vector or array input as required by the function.",
        output,
        options,
        examples,
    )


# Plotting
for name, summary, signature, inputs, output, options in [
    ("figure", "Create or activate a figure.", "figure or figure(n)", "n: optional figure number.", "Creates or activates a plotting figure. Returns no value.", "When n is omitted, creates the next figure."),
    ("close", "Close one or more figures.", "close, close(n), or close all", "n: optional figure number. all: close every figure.", "Closes the current figure, a numbered figure, or all figures. Returns no value.", "Command syntax supports close all."),
    ("plot", "Plot x-y data.", "plot(x, y)", "x, y: numeric vectors of compatible length.", "Displays or updates a plot. Returns no value.", "Uses the configured plotting backend."),
    ("title", "Set current plot title.", "title(text)", "text: string.", "Updates the current plot title. Returns no value.", "No options."),
    ("xlabel", "Set current plot x-axis label.", "xlabel(text)", "text: string.", "Updates the current x label. Returns no value.", "No options."),
    ("ylabel", "Set current plot y-axis label.", "ylabel(text)", "text: string.", "Updates the current y label. Returns no value.", "No options."),
    ("grid", "Toggle current plot grid.", "grid(value)", "value: optional logical true/false.", "Turns plot grid on or off. Returns no value.", "Defaults to true."),
    ("bode", "Plot Bode magnitude and phase diagrams for a transfer function.", ["bode(num, den)", "bode(num, den, w)"], "num, den: descending-power transfer-function coefficient vectors. w: optional frequency vector in rad/s.", "Creates magnitude and phase plots. Returns no value.", "When w is omitted, a logarithmic frequency range is chosen from poles and zeros."),
    ("nyquist", "Plot a Nyquist diagram for a transfer function.", ["nyquist(num, den)", "nyquist(num, den, w)"], "num, den: descending-power transfer-function coefficient vectors. w: optional nonnegative frequency vector in rad/s.", "Creates a Nyquist plot. Returns no value.", "When w is omitted, a logarithmic frequency range is chosen from poles and zeros."),
]:
    examples = signature if isinstance(signature, list) else [signature]
    add(name, "plotting", summary, signature, inputs, output, options, examples)


# Symbolic and type helpers
for name, summary, signature, inputs, output, options, examples in [
    ("sym", "Create or preserve a symbolic expression.", "sym(value)", "value: string, number, or symbolic value.", "Symbolic value.", "String input preserves exact text.", ["sym('1/33')"]),
    ("class", "Return MathTool type/class name.", "class(value)", "value: any MathTool value.", "Class string such as double, char, logical, sym, or struct.", "No options.", ["class([1 2])"]),
    ("solve", "Solve symbolic equations.", "solve(equations, variables, Name=Value)", "equations: symbolic equation(s). variables: optional symbolic variable(s).", "Symbolic solution, vector of solutions, or struct mapping variable names to solutions.", "Supports Real=true to filter real-valued solutions.", ["solve(x^2 - 1 == 0, x)", "solve(eqns, [u v], Real=true)"]),
    ("symvar", "List symbolic variables present in an expression.", "symvar(value)", "value: symbolic expression, equation, or array of either.", "Vector of symbolic variables.", "Variables are sorted with x, y, z, t preferred first.", ["symvar(x + y)"]),
    ("simplify", "Simplify a symbolic expression.", "simplify(expr)", "expr: symbolic expression or equation.", "Simplified symbolic expression or equation.", "Combines like terms and removes trivial operations.", ["simplify(x + x + 0)"]),
    ("collect", "Collect polynomial terms by a variable.", "collect(expr, var)", "expr: symbolic expression. var: symbolic variable.", "Symbolic expression grouped by powers of var.", "The expression must be algebraic in the selected variable.", ["collect(expand((x + 1)^2), x)"]),
    ("expand", "Expand symbolic products and powers.", "expand(expr)", "expr: symbolic expression or equation.", "Expanded symbolic expression or equation.", "Use develop(expr) as an alias.", ["expand((x + 1)^2)"]),
    ("develop", "Alias for expand.", "develop(expr)", "expr: symbolic expression or equation.", "Expanded symbolic expression or equation.", "Equivalent to expand(expr).", ["develop((x + 1)^2)"]),
    ("factor", "Factor a symbolic expression or integer.", "factor(expr)", "expr: symbolic expression, or integer >= 2.", "Factored symbolic expression, or prime factor vector for integer input.", "Symbolic input uses algebraic factorization.", ["factor(x^2 - 1)", "factor(60)"]),
    ("subs", "Substitute symbolic variables with values.", "subs(expr, var, value)", "expr: symbolic expression or equation. var: symbolic variable or vector of variables. value: replacement value or vector.", "Symbolic expression or equation after substitution.", "Variable and value vectors must have matching lengths.", ["subs(x^2 + y, x, 3)"]),
    ("coeffs", "Return polynomial coefficients.", "coeffs(expr, var)", "expr: symbolic polynomial. var: optional symbolic variable.", "Vector of coefficients ordered by descending powers.", "When var is omitted, the preferred symbolic variable is used.", ["coeffs(x^2 + 2*x + 1, x)"]),
    ("syms", "Declare symbolic variables.", "syms x y", "One or more identifier names.", "Creates symbolic variables in the current scope. Returns no value.", "Command syntax only; use spaces or commas.", ["syms x y"]),
]:
    add(name, "symbolic and type helpers", summary, signature, inputs, output, options, examples)


def help_overview():
    lines = [
        "MathTool help",
        "=============",
        "",
        "Use help functionName or help('functionName') for details.",
        "",
        "Available topics:",
    ]

    for category in sorted(HELP_CATEGORIES):
        names = ", ".join(sorted(HELP_CATEGORIES[category]))
        lines.append(f"  {category}: {names}")

    return "\n".join(lines)


def format_help(topic=None):
    if topic is None or str(topic).strip() == "":
        return help_overview()

    name = str(topic).strip().lower()
    topic_entry = HELP_TOPICS.get(name)

    if topic_entry is None:
        return (
            f"No help available for '{topic}'.\n"
            "Use help to list available topics."
        )

    lines = [
        name,
        "-" * len(name),
        f"Definition: {topic_entry['summary']}",
        "",
        "Syntax:",
    ]

    for signature in topic_entry["signatures"]:
        lines.append(f"  {signature}")

    lines.extend(
        [
            "",
            f"Inputs: {topic_entry['inputs']}",
            f"Output: {topic_entry['output']}",
            f"Options: {topic_entry['options']}",
        ]
    )

    if topic_entry["examples"]:
        lines.append("Examples:")

        for example in topic_entry["examples"]:
            lines.append(f"  {example}")

    if topic_entry["see_also"]:
        lines.append(
            "See also: "
            + ", ".join(topic_entry["see_also"])
        )

    return "\n".join(lines)
