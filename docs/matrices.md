---
id: matrices
title: Matrices
category: Matrices
summary: Build matrices, query sizes, reshape arrays, and use linear algebra helpers.
keywords: matrix, matrices, arrays, vector, linear algebra, indexing, size
aliases: matrix guide, arrays
related: zeros, ones, eye, size, reshape, eig, inv, linsolve
---

# Matrices

Create vectors and matrices with MATLAB-style brackets.

```mathtool
v = [1 2 3 4];
A = [1 2; 3 4];
```

## Construction helpers

```mathtool
Z = zeros(3, 4);
I = eye(3);
x = linspace(0, 1, 5);
```

## Size and shape

```mathtool
dims = size(A);
n = numel(A);
B = reshape([1 2 3 4], 2, 2);
```

## Indexing

Subscripts are 1-based. Use two subscripts for row and column access:

```mathtool
A = [1 2 3; 4 5 6; 7 8 9];
x = A(2, 3);
```

Colon notation selects ranges or whole dimensions:

```mathtool
row = A(2, :);
col = A(:, 3);
block = A(1:2, 2:3);
stepped = [1 2 3 4 5 6 7 8 9 10](1:2:10);
```

The `end` keyword means the last valid index in the current indexing
dimension, and it can be used in arithmetic:

```mathtool
last = A(end, end);
tail = A(end-1:end, :);
```

Single-subscript indexing uses MATLAB-style column-major order:

```mathtool
first = A(1);
fifth = A(5);
picked = A([1 5 9]);
flat = A(:);
```

Vector subscripts preserve order and repetitions:

```mathtool
rows = A([1 3], :);
cols = A(:, [1 2]);
again = A([1 1 2], :);
```

Logical masks select elements in column-major order and return a
column vector:

```mathtool
mask = A > 5;
values = A(mask);
A(A > 5 & A < 9) = 0;
```

Indexed assignment supports scalar expansion and matching-size right
hand sides:

```mathtool
A(:, 1) = 0;
A(2, :) = [10 11 12];
A(1:2, 1:2) = 7;
```

Known limits: MathTool focuses on numeric/list/NumPy-backed arrays.
Most indexing behavior is implemented for vectors and matrices; basic
multi-dimensional numeric arrays follow the same colon/range rules when
created by built-ins such as `reshape`.

## Linear algebra

```mathtool
values = eig(A).values;
x = linsolve(A, [1; 0]);
```

Related: [zeros](topic:zeros), [ones](topic:ones), [eig](topic:eig), [linsolve](topic:linsolve).
