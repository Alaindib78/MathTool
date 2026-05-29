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

Symbolic arrays are differentiated and integrated element by element:

```mathtool
A = [x x^2; sin(x) cos(x)];
dA = diff(A, x);
```

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
- `Name=Value` parser syntax is supported where MathTool already parses
  it; string/value pairs such as `"AbsTol", 1e-12` are also supported.
- `integral2("Method","tiled")` maps to the current SciPy-backed
  calculation.
- Complex contour integration is not implemented.
- Anonymous functions support MathTool expressions and closure variables,
  but not every MATLAB function-handle edge case.
