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

## Linear algebra

```mathtool
values = eig(A).values;
x = linsolve(A, [1; 0]);
```

Related: [zeros](topic:zeros), [ones](topic:ones), [eig](topic:eig), [linsolve](topic:linsolve).
