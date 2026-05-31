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
    "print",
    "console",
    "Display one or more values using readable MATLAB-style formatting.",
    "print(value1, value2, ...)",
    "valueN: any MathTool value.",
    "Writes formatted text to the console. Returns no value.",
    "Each argument is displayed on its own formatted block.",
    ["print(tf(1.5, [1 14 40.02]))"],
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
    "input",
    "console",
    "Request user input from the command window.",
    ["x = input(prompt)", "txt = input(prompt, 's')"],
    "prompt: string displayed to the user. 's': optional text mode.",
    "Evaluated value, empty matrix for blank input, or raw text in 's' mode.",
    "Without 's', the response is evaluated as a MathTool expression in the current workspace and invalid expressions re-prompt.",
    ["x = input('Value? ')", "txt = input('Name? ', 's')"],
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
add(
    "format",
    "console",
    "Set MATLAB-style numeric display and line spacing.",
    [
        "format",
        "format style",
        "format('style')",
    ],
    (
        "style: optional display style such as short, long, shortE, longE, "
        "shortG, longG, shortEng, longEng, bank, rat, hex, +, compact, "
        "loose, or default."
    ),
    "Changes display formatting for the current session. Returns no value.",
    (
        "Formatting affects presentation only. Stored values and arithmetic "
        "precision are unchanged."
    ),
    [
        "format long",
        "format shortE",
        "format compact",
    ],
    see_also=["disp", "fprintf", "formatsettings"],
)
add(
    "formatsettings",
    "console",
    "Return the active numeric format and line spacing.",
    "formatsettings()",
    "No inputs.",
    "Returns a struct-like value with NumericFormat and LineSpacing fields.",
    "Use format to change these settings.",
    ["formatsettings()"],
    see_also=["format"],
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
    ("diff", "Discrete differences for numeric arrays or symbolic derivatives for symbolic expressions.", ["diff(A)", "diff(A,n,dim)", "diff(f)", "diff(f,var,n)"], "A: numeric array. f: symbolic expression or symbolic array. var: symbolic variable. n: optional order.", "Array of differences, or symbolic derivative.", "Numeric dim is 1-based. Symbolic variables default to the first variable in the expression.", ["diff([1 4 9])", "diff(sin(x^2), x)"]),
    ("gradient", "Numerical gradient estimate.", ["gradient(A)", "gradient(A,h)", "[FX,FY] = gradient(A)"], "A: numeric vector, matrix, or array. h: optional spacing scalar/vector.", "Derivative array for vectors; tuple of derivative arrays for matrices and N-D arrays.", "For 2-D arrays, multi-output order follows MATLAB-style FX,FY.", ["gradient([1 4 9])", "[FX,FY] = gradient(M)"]),
    ("integral", "Adaptive one-dimensional numerical integration.", "integral(fun, xmin, xmax, Name, Value)", "fun: function handle @(x). xmin/xmax: numeric bounds. Name,Value options: AbsTol, RelTol, ArrayValued, Waypoints.", "Numeric integral estimate.", "Uses scipy.integrate.quad or quad_vec for ArrayValued=true.", ["integral(@(x) exp(-x.^2), 0, 1)"]),
    ("integral2", "Adaptive double numerical integration.", "integral2(fun, xmin, xmax, ymin, ymax, Name, Value)", "fun: function handle @(x,y). y bounds may be numeric or function handles.", "Numeric double-integral estimate.", "Method='tiled' is accepted as a best-effort SciPy-backed calculation.", ["integral2(@(x,y) x.^2 + y.^2, 0, 1, 0, 1)"]),
    ("cumsum", "Cumulative sum.", "cumsum(A, dim)", "A: numeric array. dim: optional 1-based dimension.", "Array of cumulative sums.", "Without dim, uses flattened order.", ["cumsum([1 2 3])"]),
    ("cumprod", "Cumulative product.", "cumprod(A, dim)", "A: numeric array. dim: optional 1-based dimension.", "Array of cumulative products.", "Without dim, uses flattened order.", ["cumprod([1 2 3])"]),
    ("trapz", "Trapezoidal numerical integration.", ["trapz(Y)", "trapz(X,Y)", "trapz(Y,dim)", "trapz(X,Y,dim)"], "Y: samples. X: optional coordinates or spacing scalar. dim: optional 1-based dimension.", "Scalar or array integral estimate.", "Defaults to the first non-singleton dimension.", ["trapz([1 4 9])", "trapz(x, y)"]),
    ("interp1", "One-dimensional linear interpolation.", "interp1(x, y, query)", "x: sample locations. y: sample values. query: scalar or vector query points.", "Interpolated scalar or array.", "Extrapolation is not currently exposed.", ["interp1([0 1], [0 10], 0.5)"]),
    ("filter", "Apply a one-dimensional digital filter.", ["filter(b, a, x)", "filter(d, x)"], "b, a: numerator and denominator coefficients. d: designfilt digital filter struct. x: signal vector or matrix.", "Filtered signal with the same shape as x.", "Uses scipy.signal.lfilter. Initial filter conditions and multi-output state return are not currently supported.", ["filter([1 1]/2, 1, [1 2 3])"]),
    ("filtfilt", "Apply zero-phase forward-backward digital filtering.", ["filtfilt(b, a, x)", "filtfilt(d, x)"], "b, a: filter coefficients. d: designfilt digital filter struct. x: signal vector or matrix.", "Zero-phase filtered signal with the same shape as x.", "Uses scipy.signal.filtfilt and falls back to one-pass filtering for very short signals.", ["b = fir1(20, 0.25); y = filtfilt(b, 1, x)"]),
    ("fir1", "Window-based FIR filter design.", ["fir1(n, Wn)", "fir1(n, Wn, type)", "fir1(n, Wn, type, window)"], "n: filter order. Wn: normalized cutoff or two-element band. type: optional high, stop, or bandpass. window: optional SciPy window name.", "Row vector of FIR numerator coefficients.", "Uses scipy.signal.firwin. The default sampling rate is 2, matching MATLAB normalized frequency units.", ["b = fir1(20, 0.4)", "b = fir1(30, [0.2 0.5], 'bandpass')"]),
    ("butter", "Butterworth digital or analog IIR filter design.", ["[b,a] = butter(n, Wn)", "[b,a] = butter(n, Wn, type)", "[b,a] = butter(n, Wn, type, 's')"], "n: filter order. Wn: normalized digital cutoff in (0,1), two-element band, or positive analog cutoff when 's' is supplied. type: optional high, stop, or bandpass.", "Numerator and denominator coefficient vectors.", "Uses scipy.signal.butter. ZPK/state-space and order-selection forms are not currently exposed.", ["[b,a] = butter(4, 0.25)", "[b,a] = butter(4, [0.2 0.4], 'bandpass')"]),
    ("cheby1", "Chebyshev Type I IIR filter design.", ["[b,a] = cheby1(n, Rp, Wp)", "[b,a] = cheby1(n, Rp, Wp, type)"], "n: order. Rp: passband ripple in dB. Wp: normalized passband edge or two-element band.", "Numerator and denominator coefficient vectors.", "Uses scipy.signal.cheby1. Analog form accepts trailing 's'.", ["[b,a] = cheby1(4, 1, 0.3)"]),
    ("cheby2", "Chebyshev Type II IIR filter design.", ["[b,a] = cheby2(n, Rs, Ws)", "[b,a] = cheby2(n, Rs, Ws, type)"], "n: order. Rs: stopband attenuation in dB. Ws: normalized stopband edge or two-element band.", "Numerator and denominator coefficient vectors.", "Uses scipy.signal.cheby2. Analog form accepts trailing 's'.", ["[b,a] = cheby2(4, 40, 0.3)"]),
    ("ellip", "Elliptic IIR filter design.", ["[b,a] = ellip(n, Rp, Rs, Wp)", "[b,a] = ellip(n, Rp, Rs, Wp, type)"], "n: order. Rp: passband ripple in dB. Rs: stopband attenuation in dB. Wp: normalized passband edge or two-element band.", "Numerator and denominator coefficient vectors.", "Uses scipy.signal.ellip. Analog form accepts trailing 's'.", ["[b,a] = ellip(4, 1, 40, 0.3)"]),
    ("hann", "Hann window.", ["hann(L)", "hann(L, 'periodic')", "hann(L, 'symmetric', 'single')"], "L: nonnegative window length. Optional mode is symmetric or periodic. Optional type is double or single.", "L-by-1 window vector.", "Uses scipy.signal.windows.hann.", ["w = hann(64)", "w = hann(64, 'periodic')"]),
    ("hamming", "Hamming window.", ["hamming(L)", "hamming(L, 'periodic')", "hamming(L, 'symmetric', 'single')"], "L: nonnegative window length. Optional mode is symmetric or periodic. Optional type is double or single.", "L-by-1 window vector.", "Uses scipy.signal.windows.hamming.", ["w = hamming(64)"]),
    ("blackman", "Blackman window.", ["blackman(L)", "blackman(L, 'periodic')", "blackman(L, 'symmetric', 'single')"], "L: nonnegative window length. Optional mode is symmetric or periodic. Optional type is double or single.", "L-by-1 window vector.", "Uses scipy.signal.windows.blackman.", ["w = blackman(64)"]),
    ("kaiser", "Kaiser window.", ["kaiser(L)", "kaiser(L, beta)", "kaiser(L, beta, 'single')"], "L: nonnegative window length. beta: optional shape parameter. Optional type is double or single.", "L-by-1 window vector.", "Uses scipy.signal.windows.kaiser. The default beta is 0.5.", ["w = kaiser(64, 8)"]),
    ("designfilt", "Design a digital FIR or IIR filter object.", ["designfilt(response, Name, Value)"], "response: lowpassfir, highpassfir, bandpassfir, bandstopfir, lowpassiir, highpassiir, bandpassiir, or bandstopiir. Name/value options include FilterOrder, CutoffFrequency, CutoffFrequency1/2, HalfPowerFrequency1/2, and SampleRate.", "Struct-like digital filter with Numerator, Denominator, Response, SampleRate, and DesignMethod fields.", "Implements a practical SciPy-backed subset of MATLAB designfilt.", ["d = designfilt('lowpassfir', 'FilterOrder', 20, 'CutoffFrequency', 0.4)"]),
    ("lowpass", "Lowpass-filter a signal.", ["lowpass(x, wpass)", "lowpass(x, fpass, fs)", "lowpass(x, fpass, fs, Name, Value)"], "x: signal vector or matrix. wpass: normalized passband in (0,1). fpass/fs: frequency and sample rate.", "Filtered signal with the same shape as x.", "Uses a Butterworth IIR filter by default and zero-phase filtering. Name/value options include ImpulseResponse and FilterOrder.", ["y = lowpass(x, 0.25)", "y = lowpass(x, 150, 1000)"]),
    ("highpass", "Highpass-filter a signal.", ["highpass(x, wpass)", "highpass(x, fpass, fs)", "highpass(x, fpass, fs, Name, Value)"], "x: signal vector or matrix. wpass or fpass/fs define the passband.", "Filtered signal with the same shape as x.", "Uses a Butterworth IIR filter by default and zero-phase filtering. Name/value options include ImpulseResponse and FilterOrder.", ["y = highpass(x, 0.25)"]),
    ("bandpass", "Bandpass-filter a signal.", ["bandpass(x, wpass)", "bandpass(x, fpass, fs)", "bandpass(x, fpass, fs, Name, Value)"], "x: signal vector or matrix. passband is a two-element increasing vector.", "Filtered signal with the same shape as x.", "Uses a Butterworth IIR filter by default and zero-phase filtering. Name/value options include ImpulseResponse and FilterOrder.", ["y = bandpass(x, [100 200], 1000)"]),
    ("bandstop", "Bandstop-filter a signal.", ["bandstop(x, wstop)", "bandstop(x, fstop, fs)", "bandstop(x, fstop, fs, Name, Value)"], "x: signal vector or matrix. stopband is a two-element increasing vector.", "Filtered signal with the same shape as x.", "Uses a Butterworth IIR filter by default and zero-phase filtering. Name/value options include ImpulseResponse and FilterOrder.", ["y = bandstop(x, [100 200], 1000)"]),
    ("fzero", "Find a real scalar root from a sign-changing interval or scalar start.", ["fzero(fun, x0)", "fzero(fun, x0, Name, Value)"], "fun: function handle returning one real scalar. x0: scalar start or two-element bracket [a b].", "Root scalar by default, or a struct with root, fval, exitflag, and output when FullOutput=true.", "Options include TolX, MaxIter, Display, FunValCheck, ReturnAll, and FullOutput. Complex and vector-valued roots are not supported.", ["f = @(x) cos(x) - x; fzero(f, [0 1])", "fzero(@(x) sin(x), 3)"]),
    ("newtons_method", "Newton-Raphson scalar root finder using a derivative function.", ["newtons_method(f, df, x0)", "newtons_method(f, df, x0, Name, Value)"], "f: function handle. df: derivative function handle. x0: scalar initial guess.", "Root scalar by default, or a root-result struct when FullOutput=true.", "Options include TolX, TolFun, MaxIter, Display, ReturnAll, FullOutput, Damping, and DerivativeZeroTolerance.", ["f = @(x) x^3 - 2*x - 5; df = @(x) 3*x^2 - 2; newtons_method(f, df, 2)"]),
    ("newton", "Alias for newtons_method.", ["newton(f, df, x0)", "newton(f, df, x0, Name, Value)"], "Same inputs as newtons_method.", "Same output as newtons_method.", "Alias only.", ["newton(@(x) cos(x)-x, @(x) -sin(x)-1, 1)"]),
    ("newton_raphson", "Alias for newtons_method.", ["newton_raphson(f, df, x0)", "newton_raphson(f, df, x0, Name, Value)"], "Same inputs as newtons_method.", "Same output as newtons_method.", "Alias only.", ["newton_raphson(@(x) cos(x)-x, @(x) -sin(x)-1, 1)"]),
    ("secant", "Secant-method scalar root finder using two starting guesses.", ["secant(f, x0, x1)", "secant(f, x0, x1, Name, Value)"], "f: function handle. x0, x1: scalar starting guesses.", "Root scalar by default, or a root-result struct when FullOutput=true.", "Options include TolX, TolFun, MaxIter, Display, ReturnAll, FullOutput, and DenominatorTolerance.", ["f = @(x) x^3 - 2*x - 5; secant(f, 1, 3)"]),
    ("fmincon", "Constrained nonlinear optimization with a MATLAB-like interface.", ["fmincon(fun, x0)", "fmincon(fun, x0, A, b)", "fmincon(fun, x0, A, b, Aeq, beq, lb, ub, nonlcon, options)", "fmincon(problem)"], "fun: scalar objective function handle. x0: numeric initial point. A,b: linear inequalities A*x <= b. Aeq,beq: linear equalities. lb,ub: bounds. nonlcon: function handle returning [c, ceq] or struct fields c and ceq.", "Optimizer x by default, or a struct with x, fval, exitflag, output, lambda, grad, and hessian when FullOutput=true.", "Uses SciPy SLSQP. Options include Algorithm, Display, MaxIterations, FunctionTolerance, ConstraintTolerance, FiniteDifferenceType, FullOutput, and ReturnAll. Complex and discrete variables are not supported.", ["fun = @(x) (x(1)-3)^2 + (x(2)-2)^2; fmincon(fun, [0 0])"]),
    ("optimoptions", "Create or update optimization options for fmincon.", ["optimoptions('fmincon')", "optimoptions('fmincon', Name, Value)", "optimoptions(existingOptions, Name, Value)"], "Solver name 'fmincon' or an existing options struct, followed by name/value options.", "Struct-like options object accepted by fmincon.", "Currently supports fmincon options and maps algorithms to the SciPy SLSQP backend.", ["opts = optimoptions('fmincon', 'Display', 'iter', 'Algorithm', 'sqp')"]),
    ("optimset", "Compatibility alias for creating fmincon optimization options.", ["optimset(Name, Value)", "optimset()"], "Name/value optimization options.", "Struct-like options object accepted by fmincon.", "Compatibility helper; use optimoptions for new scripts.", ["opts = optimset('Display', 'final')"]),
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


# Integer conversions and bit operations
for name, summary, signature, inputs, output, options, examples in [
    ("dec2hex", "Convert nonnegative decimal integers to hexadecimal text.", "dec2hex(x)", "x: integer scalar or simple integer array.", "Uppercase hexadecimal string, or a list of strings for array input.", "Negative integer formatting is not currently supported.", ["dec2hex(255)"]),
    ("dec2bin", "Convert nonnegative decimal integers to binary text.", "dec2bin(x)", "x: integer scalar or simple integer array.", "Binary string, or a list of strings for array input.", "Negative integer formatting is not currently supported.", ["dec2bin(16)"]),
    ("hex2dec", "Convert hexadecimal text to decimal integers.", "hex2dec(s)", "s: string, or simple string array. Optional 0x prefix is accepted.", "Integer value, or a list of integers for array input.", "Digits may be 0-9, A-F, or a-f.", ["hex2dec('FF')"]),
    ("bin2dec", "Convert binary text to decimal integers.", "bin2dec(s)", "s: string, or simple string array. Optional 0b prefix is accepted.", "Integer value, or a list of integers for array input.", "Digits must be 0 or 1.", ["bin2dec('1010')"]),
    ("bitand", "Bitwise AND of integer values.", "bitand(a, b)", "a, b: integer scalars or compatible integer arrays.", "Element-wise bitwise AND result.", "No options.", ["bitand(12, 10)"]),
    ("bitor", "Bitwise OR of integer values.", "bitor(a, b)", "a, b: integer scalars or compatible integer arrays.", "Element-wise bitwise OR result.", "No options.", ["bitor(12, 10)"]),
    ("bitxor", "Bitwise XOR of integer values.", "bitxor(a, b)", "a, b: integer scalars or compatible integer arrays.", "Element-wise bitwise XOR result.", "No options.", ["bitxor(12, 10)"]),
    ("bitshift", "Shift integer bits left or right.", "bitshift(a, k)", "a: integer scalar or array. k: integer shift count.", "Left shift when k is positive; right shift when k is negative.", "No options.", ["bitshift(3, 2)"]),
    ("bitget", "Get a 1-based bit from integer values.", "bitget(a, bit)", "a: integer scalar or array. bit: positive 1-based bit position.", "0 or 1 for the requested bit.", "Least significant bit is position 1.", ["bitget(10, 2)"]),
    ("bitset", "Set or clear a 1-based bit in integer values.", "bitset(a, bit, value)", "a: integer scalar or array. bit: positive 1-based bit position. value: optional logical set/clear flag.", "Integer result with the requested bit changed.", "value defaults to true.", ["bitset(8, 2, true)"]),
]:
    add(
        name,
        "integer conversions and bit operations",
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
    ("plot", "Create MATLAB-style 2-D line plots.", ["plot(Y)", "plot(X, Y)", "plot(X, Y, LineSpec)", "plot(X1, Y1, X2, Y2)", "plot(___, Name, Value)"], "X, Y: numeric scalars, vectors, or matrices. LineSpec: optional style string. Name, Value: optional line properties.", "Displays one or more lines in the active figure.", "Supports common line style, marker, color, and line property options."),
    ("histogram", "Create a MATLAB-style histogram plot.", ["histogram(X)", "histogram(X, nbins)", "histogram(X, edges)", "histogram('BinEdges', edges, 'BinCounts', counts)", "histogram(X, Name, Value)", "h = histogram(...)"], "X: numeric or logical scalar, vector, matrix, or array. nbins: positive integer. edges/counts: numeric vectors. Name, Value options are optional.", "Displays a histogram in the active axes and returns a HistogramHandle when the plot engine can return values.", "Supports NumBins, BinWidth, BinEdges, BinLimits, BinMethod, BinCounts, Normalization, DisplayStyle, Orientation, FaceColor, EdgeColor, FaceAlpha, EdgeAlpha, LineStyle, LineWidth, and DisplayName. Categorical, datetime/duration, table data, axes-target syntax, and editable histogram properties are not yet implemented."),
    ("title", "Set current plot title.", "title(text)", "text: string.", "Updates the current plot title. Returns no value.", "No options."),
    ("xlabel", "Set current plot x-axis label.", "xlabel(text)", "text: string.", "Updates the current x label. Returns no value.", "No options."),
    ("ylabel", "Set current plot y-axis label.", "ylabel(text)", "text: string.", "Updates the current y label. Returns no value.", "No options."),
    ("grid", "Toggle current plot grid.", "grid(value)", "value: optional logical true/false.", "Turns plot grid on or off. Returns no value.", "Defaults to true."),
    ("hold", "Control whether new plots replace or add to existing axes.", ["hold on", "hold off", "hold('on')", "hold('off')"], "value: optional on/off string or logical value.", "Returns the active hold state when supported by the plot engine.", "When hold is off, plot clears the active axes before drawing."),
    ("xticks", "Set or query x-axis tick positions.", ["xticks(values)", "xticks()", "xticks('auto')", "xticks('manual')", "xticks('mode')"], "values: numeric vector or empty array.", "Returns tick values or mode for query forms. Set forms return no value.", "Operates on the current axes."),
    ("xticklabels", "Set or query x-axis tick labels.", ["xticklabels(labels)", "xticklabels('auto')", "xticklabels('manual')", "xticklabels('mode')"], "labels: string arguments or string vector.", "Returns labels or mode for query forms. Set forms return no value.", "Fewer labels than ticks are padded with empty labels."),
    ("yticks", "Set or query y-axis tick positions.", ["yticks(values)", "yticks()", "yticks('auto')", "yticks('manual')", "yticks('mode')"], "values: numeric vector or empty array.", "Returns tick values or mode for query forms. Set forms return no value.", "Operates on the current axes."),
    ("yticklabels", "Set or query y-axis tick labels.", ["yticklabels(labels)", "yticklabels('auto')", "yticklabels('manual')", "yticklabels('mode')"], "labels: string arguments or string vector.", "Returns labels or mode for query forms. Set forms return no value.", "Fewer labels than ticks are padded with empty labels."),
    ("xline", "Draw vertical reference line(s).", ["xline(x)", "xline(x, LineSpec)", "xline(x, LineSpec, label)", "xline(x, Name, Value)"], "x: scalar or vector. LineSpec and label are optional.", "Returns matplotlib line handle(s) when supported.", "Supports Color, Alpha, LineWidth, DisplayName, and label alignment options."),
    ("yline", "Draw horizontal reference line(s).", ["yline(y)", "yline(y, LineSpec)", "yline(y, LineSpec, label)", "yline(y, Name, Value)"], "y: scalar or vector. LineSpec and label are optional.", "Returns matplotlib line handle(s) when supported.", "Supports Color, Alpha, LineWidth, DisplayName, and label alignment options."),
    ("legend", "Create, show, hide, or remove the current axes legend.", ["legend()", "legend(label1, label2)", "legend(labels)", "legend('off')", "legend(..., 'Location', loc)"], "labels: optional string labels. Name/value options are optional.", "Returns a matplotlib legend handle when supported.", "Supports common MATLAB locations, horizontal orientation, font size, text color, and box on/off."),
    ("subplot", "Create or select axes in a tiled figure layout.", ["subplot(m, n, p)", "subplot(m, n, p, 'replace')", "subplot('Position', [left bottom width height])"], "m, n: grid size. p: one-based subplot index or rectangular span vector.", "Returns an axes handle when supported.", "Subsequent plot helper commands target the selected axes."),
    ("axis", "Set or query current axes limits, scaling, direction, and visibility.", ["axis()", "axis([xmin xmax ymin ymax])", "axis tight", "axis equal", "axis auto", "axis manual", "axis off"], "limits: numeric vector. option: style, mode, y direction, or visibility.", "Query form returns current limits. Set forms return no value.", "Supports common MATLAB options: auto, manual, auto x/y/xy, tight, padded, tickaligned, equal, image, square, fill, normal, vis3d, ij, xy, on, off."),
    ("bode", "Plot Bode magnitude and phase diagrams for an LTI model or transfer function.", ["bode(sys)", "bode(sys, w)", "bode(num, den)", "bode(num, den, w)"], "sys: LTI model. num, den: descending-power coefficient vectors. w: optional frequency vector in rad/s.", "Creates magnitude and phase plots. Returns no value.", "LTI model analysis uses scipy.signal. Coefficient-vector form is kept for compatibility."),
    ("nyquist", "Plot a Nyquist diagram for a transfer function.", ["nyquist(num, den)", "nyquist(num, den, w)"], "num, den: descending-power transfer-function coefficient vectors. w: optional nonnegative frequency vector in rad/s.", "Creates a Nyquist plot. Returns no value.", "When w is omitted, a logarithmic frequency range is chosen from poles and zeros."),
]:
    examples = signature if isinstance(signature, list) else [signature]
    add(name, "plotting", summary, signature, inputs, output, options, examples)


# Control systems
for name, summary, signature, inputs, output, options, examples in [
    (
        "tf",
        "Create or convert a SISO transfer-function LTI model.",
        ["tf(num, den)", "tf(num, den, Ts)", "tf(sys)", "tf('s')"],
        "num, den: numeric coefficient vectors or scalars. Ts: optional nonnegative sample time. sys: LTI model.",
        "TransferFunctionModel object.",
        "SISO only. tf('s') enables transfer-variable arithmetic.",
        ["sys = tf(1.5, [1 14 40.02])", "s = tf('s'); G = 1/(s + 1)"],
    ),
    (
        "ss",
        "Create or convert a state-space LTI model.",
        ["ss(A, B, C, D)", "ss(A, B, C, D, Ts)", "ss(sys)"],
        "A, B, C, D: state-space matrices. Ts: optional nonnegative sample time. sys: LTI model.",
        "StateSpaceModel object.",
        "A must be square; dimensions must match state-space equations.",
        ["sys = ss(A, B, C, D)", "tf_sys = tf(sys)"],
    ),
    (
        "zpk",
        "Create or convert a zero-pole-gain LTI model.",
        ["zpk(z, p, k)", "zpk(z, p, k, Ts)", "zpk(sys)"],
        "z: zero vector. p: pole vector. k: scalar gain. Ts: optional nonnegative sample time. sys: LTI model.",
        "ZeroPoleGainModel object.",
        "SISO only for conversion to transfer function.",
        ["sys = zpk([], [-9.996 -4.004], 1.5)"],
    ),
    (
        "frd",
        "Create a frequency-response data model.",
        ["frd(response, w)", "frd(response, w, Ts)"],
        "response: complex response samples. w: positive frequency vector in rad/s. Ts: optional sample time.",
        "FrequencyResponseModel object.",
        "Initial FRD support is SISO and interpolation-based.",
        ["H = frd([1 0.5], [1 10])"],
    ),
    (
        "get",
        "Return readable properties for an object, LTI model, or struct.",
        "get(obj)",
        "obj: HistogramHandle, LTI model, or struct.",
        "Struct-like dictionary of properties.",
        "Object properties are read-only in the variable editor initially.",
        ["get(sys)", "sys.A", "get(h)"],
    ),
    (
        "pole",
        "Return poles of an LTI model.",
        "pole(sys)",
        "sys: LTI model.",
        "Vector of pole locations.",
        "State-space poles are eigenvalues of A.",
        ["p = pole(sys)"],
    ),
    (
        "zero",
        "Return zeros of an LTI model.",
        "zero(sys)",
        "sys: LTI model.",
        "Vector of zero locations.",
        "State-space zeros are computed by converting to transfer function.",
        ["z = zero(sys)"],
    ),
    (
        "minreal",
        "Cancel near-matching pole-zero pairs in a SISO transfer function.",
        ["minreal(sys)", "minreal(sys, tol)"],
        "sys: LTI model. tol: optional cancellation tolerance.",
        "Simplified TransferFunctionModel.",
        "Approximate educational implementation.",
        ["G = minreal((s + 1)/(s + 1))"],
    ),
    (
        "damp",
        "Return pole damping information.",
        "damp(sys)",
        "sys: LTI model.",
        "List of structs with Pole, Damping, and Frequency fields.",
        "Discrete-time damping uses logarithmic pole mapping.",
        ["damp(sys)"],
    ),
    (
        "dcgain",
        "Return DC gain of an LTI model.",
        "dcgain(sys)",
        "sys: LTI model.",
        "Scalar or matrix DC gain.",
        "Raises an error for singular DC denominator cases.",
        ["k = dcgain(sys)"],
    ),
    (
        "isstable",
        "Test LTI model stability.",
        "isstable(sys)",
        "sys: LTI model.",
        "Logical true for stable systems.",
        "Continuous-time checks real(p)<0; discrete-time checks abs(p)<1.",
        ["isstable(sys)"],
    ),
    (
        "step",
        "Plot the step response of an LTI model.",
        ["step(sys)", "step(sys, t)"],
        "sys: LTI model. t: optional time vector.",
        "Creates a time-domain response plot. Returns no value.",
        "Uses scipy.signal.step or scipy.signal.dstep.",
        ["step(sys)"],
    ),
    (
        "impulse",
        "Plot the impulse response of an LTI model.",
        ["impulse(sys)", "impulse(sys, t)"],
        "sys: LTI model. t: optional time vector.",
        "Creates a time-domain response plot. Returns no value.",
        "Uses scipy.signal.impulse or scipy.signal.dimpulse.",
        ["impulse(sys)"],
    ),
    (
        "initial",
        "Plot state-space initial-condition response.",
        ["initial(sys, x0)", "initial(sys, x0, t)"],
        "sys: LTI model. x0: initial state vector. t: optional time vector.",
        "Creates an embedded plot. Returns no value.",
        "Uses scipy.signal lsim/dlsim internally.",
        ["initial(sys, [1; 0])"],
    ),
    (
        "lsim",
        "Plot simulated response to an arbitrary input.",
        "lsim(sys, u, t)",
        "sys: LTI model. u: input samples. t: time vector.",
        "Creates an embedded plot. Returns no value.",
        "SISO and basic state-space systems are supported.",
        ["lsim(sys, sin(t), t)"],
    ),
    (
        "stepinfo",
        "Estimate common step-response metrics.",
        ["stepinfo(sys)", "stepinfo(sys, t)"],
        "sys: LTI model. t: optional time vector.",
        "Struct-like value with RiseTime, SettlingTime, Overshoot, Peak, and related fields.",
        "SISO educational estimate.",
        ["info = stepinfo(sys)"],
    ),
    (
        "bodemag",
        "Plot Bode magnitude of an LTI model.",
        ["bodemag(sys)", "bodemag(sys, w)"],
        "sys: LTI model. w: optional frequency vector.",
        "Creates an embedded magnitude plot.",
        "SISO only.",
        ["bodemag(sys)"],
    ),
    (
        "freqresp",
        "Evaluate complex frequency response.",
        "freqresp(sys, w)",
        "sys: LTI model. w: frequency vector in rad/s.",
        "Complex response vector.",
        "SISO only.",
        ["H = freqresp(sys, [1 10 100])"],
    ),
    (
        "bandwidth",
        "Estimate -3 dB bandwidth.",
        "bandwidth(sys)",
        "sys: LTI model.",
        "Estimated bandwidth in rad/s.",
        "SISO stable-system approximation.",
        ["bw = bandwidth(sys)"],
    ),
    (
        "margin",
        "Estimate gain and phase margins.",
        ["margin(sys)", "margin(sys, w)"],
        "sys: LTI model. w: optional frequency vector.",
        "Struct-like value with GainMargin, PhaseMargin, GMFrequency, and PMFrequency.",
        "Dense-grid approximation inspired by MATLAB margin.",
        ["m = margin(G)"],
    ),
    (
        "allmargin",
        "Return stability-margin summary.",
        ["allmargin(sys)", "allmargin(sys, w)"],
        "sys: LTI model. w: optional frequency vector.",
        "Struct-like margin summary including Stable.",
        "Approximate SISO implementation.",
        ["m = allmargin(G)"],
    ),
    (
        "rlocus",
        "Plot root locus of a SISO transfer function.",
        ["rlocus(sys)", "rlocus(sys, k)"],
        "sys: LTI model. k: optional gain vector.",
        "Struct-like value with roots and gains, plus embedded plot.",
        "SISO only.",
        ["rlocus(G, 0:0.1:100)"],
    ),
    (
        "feedback",
        "Form negative or positive feedback interconnection.",
        ["feedback(sys)", "feedback(sys1, sys2)", "feedback(sys1, sys2, sign)"],
        "sys1, sys2: LTI models or scalar gains. sign: -1 or +1.",
        "Closed-loop TransferFunctionModel.",
        "SISO transfer functions only.",
        ["T = feedback(C*G, 1)"],
    ),
    (
        "series",
        "Connect two SISO systems in series.",
        "series(sys1, sys2)",
        "sys1, sys2: LTI models or scalar gains.",
        "Product TransferFunctionModel.",
        "Equivalent to sys1 * sys2 for supported transfer functions.",
        ["G = series(G1, G2)"],
    ),
    (
        "parallel",
        "Connect two SISO systems in parallel.",
        "parallel(sys1, sys2)",
        "sys1, sys2: LTI models or scalar gains.",
        "Sum TransferFunctionModel.",
        "Equivalent to sys1 + sys2 for supported transfer functions.",
        ["G = parallel(G1, G2)"],
    ),
    (
        "ctrb",
        "Build controllability matrix.",
        ["ctrb(A, B)", "ctrb(sys)"],
        "A, B: state matrices, or sys: state-space model.",
        "Controllability matrix.",
        "Use rank(ctrb(...)) to test controllability.",
        ["rank(ctrb(sys))"],
    ),
    (
        "obsv",
        "Build observability matrix.",
        ["obsv(A, C)", "obsv(sys)"],
        "A, C: state/output matrices, or sys: state-space model.",
        "Observability matrix.",
        "Use rank(obsv(...)) to test observability.",
        ["rank(obsv(sys))"],
    ),
    (
        "gram",
        "Compute controllability or observability Gramian.",
        ["gram(sys, 'c')", "gram(sys, 'o')"],
        "sys: stable state-space model. kind: 'c' or 'o'.",
        "Gramian matrix.",
        "Continuous-time stable systems only.",
        ["Wc = gram(sys, 'c')"],
    ),
    (
        "lqr",
        "Design a continuous-time LQR state-feedback gain.",
        "lqr(A, B, Q, R)",
        "A, B: state/input matrices. Q, R: cost matrices.",
        "Struct-like value with K, S, and P fields.",
        "Uses scipy.linalg.solve_continuous_are.",
        ["result = lqr(A, B, Q, R)"],
    ),
    (
        "pid",
        "Create a continuous-time PID controller transfer function.",
        "pid(Kp, Ki, Kd)",
        "Kp, Ki, Kd: controller gains.",
        "TransferFunctionModel controller.",
        "Uses C(s) = (Kd*s^2 + Kp*s + Ki)/s.",
        ["C = pid(1, 0.5, 0.1)"],
    ),
    (
        "c2d",
        "Convert a continuous-time LTI model to discrete time.",
        ["c2d(sys, Ts)", "c2d(sys, Ts, method)"],
        "sys: LTI model. Ts: positive sample time. method: zoh, foh, tustin, or bilinear.",
        "Discrete-time StateSpaceModel.",
        "Uses scipy.signal.cont2discrete.",
        ["sysd = c2d(sys, 0.01, 'tustin')"],
    ),
]:
    add(
        name,
        "control systems",
        summary,
        signature,
        inputs,
        output,
        options,
        examples,
    )

for name, summary, signature, inputs, output, options, examples in [
    ("nichols", "Plot Nichols chart for an LTI model.", ["nichols(sys)", "nichols(sys, w)"], "sys: LTI model. w: optional frequency vector.", "Creates an embedded phase-vs-magnitude plot.", "SISO only.", ["nichols(sys)"]),
    ("sigma", "Plot singular-value magnitude approximation.", ["sigma(sys)", "sigma(sys, w)"], "sys: LTI model. w: optional frequency vector.", "Creates an embedded magnitude plot.", "Currently SISO magnitude only.", ["sigma(sys)"]),
    ("append", "Append systems into a block-diagonal state-space model.", "append(sys1, sys2, ...)", "Two or more LTI models.", "StateSpaceModel with block-diagonal A, B, C, and D.", "Sample times must match.", ["big = append(sys1, sys2)"]),
    ("lyap", "Solve continuous Lyapunov equation.", "lyap(A, Q)", "A, Q: numeric matrices.", "Matrix X solving A*X + X*A' + Q = 0.", "Uses scipy.linalg.", ["X = lyap(A, Q)"]),
    ("dlyap", "Solve discrete Lyapunov equation.", "dlyap(A, Q)", "A, Q: numeric matrices.", "Solution matrix X.", "Uses scipy.linalg.", ["X = dlyap(A, Q)"]),
    ("care", "Solve continuous algebraic Riccati equation.", "care(A, B, Q, R)", "A, B, Q, R: numeric matrices.", "Solution matrix X.", "Uses scipy.linalg.solve_continuous_are.", ["X = care(A, B, Q, R)"]),
    ("dare", "Solve discrete algebraic Riccati equation.", "dare(A, B, Q, R)", "A, B, Q, R: numeric matrices.", "Solution matrix X.", "Uses scipy.linalg.solve_discrete_are.", ["X = dare(A, B, Q, R)"]),
    ("place", "Place closed-loop poles by state feedback.", "place(A, B, poles)", "A, B: numeric matrices. poles: desired pole vector.", "Gain matrix K.", "Uses scipy.signal.place_poles.", ["K = place(A, B, [-1 -2])"]),
    ("acker", "Alias for pole placement.", "acker(A, B, poles)", "A, B: numeric matrices. poles: desired pole vector.", "Gain matrix K.", "Delegates to place.", ["K = acker(A, B, [-1 -2])"]),
    ("dlqr", "Design a discrete-time LQR state-feedback gain.", "dlqr(A, B, Q, R)", "A, B: state/input matrices. Q, R: cost matrices.", "Struct-like value with K, S, and P fields.", "Uses scipy.linalg.solve_discrete_are.", ["result = dlqr(A, B, Q, R)"]),
    ("pidtune", "Create an educational PID tuning approximation.", ["pidtune(sys)", "pidtune(sys, type)"], "sys: LTI model. type: P, PI, or PID.", "PID TransferFunctionModel.", "Heuristic only, not MATLAB's robust tuner.", ["C = pidtune(G, 'PI')"]),
    ("d2c", "Convert a discrete-time model to continuous time.", ["d2c(sys)", "d2c(sys, method)"], "sys: discrete-time LTI model.", "Continuous-time model when supported.", "Currently reports a clear unsupported-operation error.", ["d2c(sysd)"]),
    ("isdt", "Test whether an LTI model is discrete-time.", "isdt(sys)", "sys: LTI model.", "Logical true when Ts > 0.", "No options.", ["isdt(sys)"]),
    ("isct", "Test whether an LTI model is continuous-time.", "isct(sys)", "sys: LTI model.", "Logical true when Ts == 0.", "No options.", ["isct(sys)"]),
]:
    add(name, "control systems", summary, signature, inputs, output, options, examples)


# Symbolic and type helpers
for symbolic_entry in [
    ("sym", "Create or preserve a symbolic expression.", "sym(value)", "value: string, number, or symbolic value.", "Symbolic value.", "String input preserves exact text.", ["sym('1/33')"]),
    ("struct", "Create a MATLAB-style struct from name/value pairs.", "struct('field', value, ...)", "Field names must be strings. Values may be numbers, strings, arrays, logicals, structs, or expressions.", "Struct value with the requested fields.", "Use struct() to create an empty struct. Dot assignment also creates structs.", ["struct('name', 'Alice', 'age', 30)", "s.x = 5"]),
    ("class", "Return MathTool type/class name.", "class(value)", "value: any MathTool value.", "Class string such as double, char, logical, sym, or struct.", "No options.", ["class([1 2])"]),
    ("int", "Integrate symbolic expressions.", ["int(expr)", "int(expr,var)", "int(expr,a,b)", "int(expr,var,a,b)"], "expr: symbolic expression or symbolic array. var: optional symbolic variable. a,b: optional bounds.", "Symbolic antiderivative or definite integral.", "Hold=true returns an unevaluated symbolic integral. MATLAB analytic-constraint flags are accepted as best-effort options.", ["int(x^2, x)", "int(sin(x), x, 0, pi)"]),
    ("limit", "Compute MATLAB-style symbolic limits.", ["limit(expr)", "limit(expr,a)", "limit(expr,var,a)", "limit(expr,var,a,'left')", "limit(expr,var,a,'right')"], "expr: symbolic expression or symbolic array. var: optional symbolic variable. a: limit point such as 0, Inf, -Inf, or a symbolic expression.", "Symbolic limit result, or symbolic array with limits applied element-wise.", "Two-sided limits compare left and right limits and return NaN when they differ. Assumptions and full multivariable path limits are limited by SymPy support.", ["limit(sin(x)/x)", "limit(1/x, x, 0, 'right')", "limit(x/abs(x), x, 0)", "limit([(1+a/x)^x exp(-x)], x, Inf)"], ["diff", "int", "sym", "syms", "symvar", "simplify"]),
    ("laplace", "Compute the symbolic Laplace transform.", ["laplace(f)", "laplace(f,transVar)", "laplace(f,var,transVar)"], "f: symbolic-compatible expression or array. var: optional independent variable. transVar: optional transform variable.", "Symbolic transform, element-wise array of transforms, or an unevaluated laplace call.", "Defaults are t to s; if t is absent MathTool uses symvar-style variable selection. SymPy may leave difficult transforms unevaluated.", ["laplace(sin(t), t, s)", "laplace(exp(-2*t))"], ["ilaplace", "fourier", "ztrans", "diff", "int", "limit", "sympref"]),
    ("ilaplace", "Compute the inverse symbolic Laplace transform.", ["ilaplace(F)", "ilaplace(F,transVar)", "ilaplace(F,var,transVar)"], "F: symbolic-compatible expression or array. var: optional transform-domain variable. transVar: optional output variable.", "Symbolic inverse transform, element-wise array, or an unevaluated ilaplace call.", "Defaults are s to t; unilateral Laplace behavior follows SymPy and may differ from MATLAB for assumptions.", ["ilaplace(1/s^2, s, t)", "ilaplace(1/(s + 2))"], ["laplace", "fourier", "ifourier", "simplify"]),
    ("fourier", "Compute the symbolic Fourier transform.", ["fourier(f)", "fourier(f,transVar)", "fourier(f,var,transVar)"], "f: symbolic-compatible expression or array. var: optional independent variable. transVar: optional frequency variable.", "Symbolic Fourier transform, element-wise array, or an unevaluated fourier call.", "Uses MATLAB-like default Fourier parameters [1 -1]. sympref can store alternate parameters, but some results depend on SymPy support.", ["fourier(exp(-x^2), x, w)", "fourier(f, w)"], ["ifourier", "laplace", "sympref", "simplify"]),
    ("ifourier", "Compute the inverse symbolic Fourier transform.", ["ifourier(F)", "ifourier(F,transVar)", "ifourier(F,var,transVar)"], "F: symbolic-compatible expression or array. var: optional frequency variable. transVar: optional output variable.", "Symbolic inverse Fourier transform, element-wise array, or an unevaluated ifourier call.", "Defaults are w to x. Parameterized Fourier preferences are best-effort.", ["ifourier(exp(-w^2/4), w, x)"], ["fourier", "laplace", "sympref", "simplify"]),
    ("ztrans", "Compute the unilateral symbolic Z-transform.", ["ztrans(f)", "ztrans(f,transVar)", "ztrans(f,var,transVar)"], "f: symbolic-compatible sequence expression or array. var: optional sequence variable. transVar: optional transform variable.", "Symbolic Z-transform, element-wise array, or an unevaluated ztrans call.", "Defaults are n to z. Implemented with symbolic summation, so difficult sequences may remain unevaluated.", ["ztrans(2^n, n, z)", "ztrans(n, n, z)"], ["iztrans", "laplace", "fourier", "simplify"]),
    ("iztrans", "Compute the inverse symbolic Z-transform.", ["iztrans(F)", "iztrans(F,transVar)", "iztrans(F,var,transVar)"], "F: symbolic-compatible transform expression or array. var: optional transform-domain variable. transVar: optional sequence variable.", "Symbolic inverse Z-transform, element-wise array, or an unevaluated iztrans call.", "Defaults are z to n. Common rational forms are handled by residues; unsupported forms stay unevaluated.", ["iztrans(z/(z-2), z, n)", "iztrans(2*z/(z-2)^2, z, n)"], ["ztrans", "simplify", "symvar"]),
    ("solve", "Solve symbolic equations.", "solve(equations, variables, Name=Value)", "equations: symbolic equation(s). variables: optional symbolic variable(s).", "Symbolic solution, vector of solutions, or struct mapping variable names to solutions.", "Supports Real=true to filter real-valued solutions.", ["solve(x^2 - 1 == 0, x)", "solve(eqns, [u v], Real=true)"]),
    ("symvar", "List symbolic variables present in an expression.", "symvar(value)", "value: symbolic expression, equation, or array of either.", "Vector of symbolic variables.", "Variables are sorted with x, y, z, t preferred first.", ["symvar(x + y)"]),
    ("dirac", "Create a symbolic Dirac delta expression.", "dirac(x)", "x: symbolic-compatible scalar or array.", "Symbolic Dirac delta expression.", "Maps to SymPy DiracDelta and displays as dirac.", ["dirac(t - a)"], ["laplace", "ilaplace", "heaviside"]),
    ("heaviside", "Create a symbolic Heaviside step expression.", "heaviside(x)", "x: symbolic-compatible scalar or array.", "Symbolic Heaviside expression.", "Maps to SymPy Heaviside and displays as heaviside.", ["heaviside(t - a)"], ["laplace", "ilaplace", "dirac"]),
    ("kroneckerDelta", "Create a symbolic Kronecker delta expression.", "kroneckerDelta(n,k)", "n, k: symbolic-compatible scalar or array values.", "Symbolic Kronecker delta expression.", "Nonscalar arguments use scalar expansion when sizes are compatible.", ["kroneckerDelta(n, 0)"], ["ztrans", "iztrans"]),
    ("rectangularPulse", "Create a symbolic rectangular pulse expression.", ["rectangularPulse(x)", "rectangularPulse(a,b,x)"], "x: symbolic variable or expression. a,b: optional interval endpoints.", "Piecewise symbolic rectangular pulse.", "The one-argument form uses the interval [-1/2, 1/2].", ["rectangularPulse(t)", "rectangularPulse(0, 1, t)"], ["triangularPulse", "heaviside"]),
    ("triangularPulse", "Create a symbolic triangular pulse expression.", ["triangularPulse(x)", "triangularPulse(a,b,c,x)"], "x: symbolic variable or expression. a,b,c: optional left, center, and right points.", "Piecewise symbolic triangular pulse.", "The one-argument form uses left -1, center 0, and right 1.", ["triangularPulse(t)", "triangularPulse(0, 1, 2, t)"], ["rectangularPulse", "heaviside"]),
    ("sympref", "Set or query symbolic preferences.", ["sympref()", "sympref('FourierParameters')", "sympref('FourierParameters', value)", "sympref('default')"], "Preference name and optional value. FourierParameters accepts a two-element vector or 'default'.", "Preference value, all preferences, or no value when setting.", "Fourier parameter support is best-effort; default [1 -1] is fully supported for common transforms.", ["sympref('FourierParameters', [1 1])", "sympref('FourierParameters', 'default')"], ["fourier", "ifourier", "sym"]),
    ("simplify", "Simplify a symbolic expression.", "simplify(expr)", "expr: symbolic expression or equation.", "Simplified symbolic expression or equation.", "Combines like terms and removes trivial operations.", ["simplify(x + x + 0)"]),
    ("collect", "Collect polynomial terms by a variable.", "collect(expr, var)", "expr: symbolic expression. var: symbolic variable.", "Symbolic expression grouped by powers of var.", "The expression must be algebraic in the selected variable.", ["collect(expand((x + 1)^2), x)"]),
    ("expand", "Expand symbolic products and powers.", "expand(expr)", "expr: symbolic expression or equation.", "Expanded symbolic expression or equation.", "Use develop(expr) as an alias.", ["expand((x + 1)^2)"]),
    ("develop", "Alias for expand.", "develop(expr)", "expr: symbolic expression or equation.", "Expanded symbolic expression or equation.", "Equivalent to expand(expr).", ["develop((x + 1)^2)"]),
    ("factor", "Factor a symbolic expression or integer.", "factor(expr)", "expr: symbolic expression, or integer >= 2.", "Factored symbolic expression, or prime factor vector for integer input.", "Symbolic input uses algebraic factorization.", ["factor(x^2 - 1)", "factor(60)"]),
    ("subs", "Substitute symbolic variables with values.", "subs(expr, var, value)", "expr: symbolic expression or equation. var: symbolic variable or vector of variables. value: replacement value or vector.", "Symbolic expression or equation after substitution.", "Variable and value vectors must have matching lengths.", ["subs(x^2 + y, x, 3)"]),
    ("coeffs", "Return polynomial coefficients.", "coeffs(expr, var)", "expr: symbolic polynomial. var: optional symbolic variable.", "Vector of coefficients ordered by descending powers.", "When var is omitted, the preferred symbolic variable is used.", ["coeffs(x^2 + 2*x + 1, x)"]),
    ("pretty", "Render a symbolic expression using pretty text.", "pretty(expr)", "expr: symbolic expression.", "Formatted text, or printed output in the command window.", "Formatting comes from SymPy.", ["pretty((x + 1)^2)"]),
    ("syms", "Declare symbolic variables.", ["syms x y", "syms('x','y')"], "One or more identifier names, or string names in function-call form.", "Creates symbolic variables in the current scope.", "Command syntax returns no value; function-call syntax returns the created symbolic value(s).", ["syms x y", "syms('x','y')"]),
]:
    if len(symbolic_entry) == 7:
        (
            name,
            summary,
            signature,
            inputs,
            output,
            options,
            examples,
        ) = symbolic_entry
        see_also = None
    else:
        (
            name,
            summary,
            signature,
            inputs,
            output,
            options,
            examples,
            see_also,
        ) = symbolic_entry

    add(
        name,
        "symbolic and type helpers",
        summary,
        signature,
        inputs,
        output,
        options,
        examples,
        see_also=see_also,
    )


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

    requested_name = str(topic).strip()
    name = requested_name.lower()
    topic_name = requested_name if requested_name in HELP_TOPICS else name
    topic_entry = HELP_TOPICS.get(topic_name)

    if topic_entry is None:
        for candidate in HELP_TOPICS:
            if candidate.lower() == name:
                topic_name = candidate
                topic_entry = HELP_TOPICS[candidate]
                break

    if topic_entry is None:
        return (
            f"No help available for '{topic}'.\n"
            "Use help to list available topics."
        )

    lines = [
        topic_name,
        "-" * len(topic_name),
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
