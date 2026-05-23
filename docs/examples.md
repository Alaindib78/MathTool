---
id: examples
title: Examples
category: Examples
summary: Starter scripts for plotting, matrices, symbolic math, and debugging.
keywords: examples, scripts, plotting, matrix, symbolic, debugging
aliases: sample code, demos
related: plotting-guide, matrices, debugging, functions
---

# Examples

## Plot a sine wave

```mathtool
x = linspace(0, 2*pi, 200);
y = sin(x);
plot(x, y);
title('Sine wave');
xlabel('x');
ylabel('sin(x)');
```

## Solve a linear system

```mathtool
A = [3 1; 1 2];
b = [9; 8];
x = linsolve(A, b);
disp(x);
```

## Symbolic solve

```mathtool
syms x
solutions = solve(x^2 - 1 == 0, x);
disp(solutions);
```

Related: [Plotting Guide](topic:plotting-guide), [Matrices](topic:matrices), [Functions](topic:functions).
