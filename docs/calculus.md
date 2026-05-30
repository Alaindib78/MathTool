# Calculus

MathTool supports a practical MATLAB-style subset of symbolic and
numerical calculus.

## Symbolic Calculus

Create symbolic variables with command syntax or function-call syntax:

```mathtool
syms x y
t = sym("t");
syms("u", "v");
```

Differentiate symbolic expressions:

```mathtool
x = sym("x");

df = diff(sin(x^2), x);
d4 = diff(x^6, x, 4);
```

Integrate symbolic expressions:

```mathtool
F = int(x^2, x);
q = int(sin(x), x, 0, pi);
```

Compute symbolic limits:

```mathtool
L1 = limit(sin(x)/x);
L2 = limit(sin(x)/x, x, 0);
L3 = limit(1/x, x, 0, "right");
L4 = limit(x/abs(x), x, 0);
```

`limit(expr)` uses the default symbolic variable and approaches 0.
`limit(expr, a)` approaches `a`. Use `"left"` or `"right"` for
one-sided limits. If the left and right limits differ, MathTool returns
`NaN` for the two-sided limit.

Symbolic arrays are differentiated, integrated, and limited element by
element:

```mathtool
A = [x x^2; sin(x) cos(x)];
dA = diff(A, x);

M = [sin(x)/x 1/x; x^2 cos(x)];
LM = limit(M, x, 0, "right");
```

## Symbolic Transforms

MathTool supports MATLAB-style symbolic transform helpers:

```mathtool
syms t s x w n z

F = laplace(sin(t), t, s);
f = ilaplace(1/s^2, s, t);

G = fourier(exp(-x^2), x, w);
g = ifourier(exp(-w^2/4), w, x);

Z = ztrans(2^n, n, z);
seq = iztrans(2*z/(z - 2)^2, z, n);
```

Default variables follow MATLAB conventions: `laplace` uses `t` to `s`,
`ilaplace` uses `s` to `t`, `fourier` uses the first symbolic variable
to `w`, `ifourier` uses `w` to `x`, `ztrans` uses `n` to `z`, and
`iztrans` uses `z` to `n`.

All transform helpers support scalar expansion and element-wise symbolic
arrays:

```mathtool
syms x y a b c d w z
M = [exp(x) 1; sin(y) 1i*z];
vars = [w x; y z];
transVars = [a b; c d];

L = laplace(M, vars, transVars);
```

Distribution helpers are available for symbolic transform workflows:

```mathtool
dirac(t)
heaviside(t)
kroneckerDelta(n, 0)
```

Fourier preferences can be stored with `sympref`:

```mathtool
sympref("FourierParameters", [1 1]);
sympref("FourierParameters", "default");
```

The default Fourier parameters `[1 -1]` are the most thoroughly
supported. Difficult transforms return an unevaluated symbolic call such
as `laplace(f(t), t, s)` instead of aborting execution.

Symbolic math is powered by SymPy, so simplification and formatting can
differ from MATLAB.

## Numerical Integration

Anonymous function handles use MATLAB-style syntax:

```mathtool
f = @(x) exp(-x.^2);
q = integral(f, 0, 1);
```

Use name/value options for tolerances:

```mathtool
q = integral(@(x) log(x), 0, 1, "AbsTol", 1e-12, "RelTol", 0);
```

Double integrals use `integral2`:

```mathtool
q = integral2(@(x,y) x.^2 + y.^2, 0, 1, 0, 1);

ymax = @(x) 1 - x;
tri = integral2(@(x,y) x + y, 0, 1, 0, ymax);
```

`integral` and `integral2` use SciPy adaptive quadrature.

## Trapezoids And Gradients

`trapz` supports unit spacing, coordinate vectors, spacing scalars, and
1-based dimensions:

```mathtool
trapz([1 4 9 16 25]);
trapz(x, y);
trapz(M, 2);
```

`gradient` supports vector and matrix inputs:

```mathtool
gx = gradient(1:10);

M = [1 2 3; 4 5 6];
[FX, FY] = gradient(M);
```

## Limitations

- Symbolic assumptions are limited.
- Multivariable limits are not full path-independent limits; apply
  iterated single-variable limits explicitly.
- Some symbolic transforms remain unevaluated when SymPy cannot solve
  them. Fourier preference support beyond the default parameters is
  best-effort.
- `ztrans` uses unilateral symbolic summation. `iztrans` supports common
  rational forms using residues and may leave harder inputs unevaluated.
- `Name=Value` parser syntax is supported where MathTool already parses
  it; string/value pairs such as `"AbsTol", 1e-12` are also supported.
- `integral2("Method","tiled")` maps to the current SciPy-backed
  calculation.
- Complex contour integration is not implemented.
- Anonymous functions support MathTool expressions and closure variables,
  but not every MATLAB function-handle edge case.
