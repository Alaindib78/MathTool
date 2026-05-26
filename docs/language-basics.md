---
id: language-basics
title: Language Basics
category: Language Basics
summary: Core MathTool syntax for expressions, statements, comments, and command-style calls.
keywords: syntax, expressions, statements, comments, command syntax, semicolon
aliases: basics, getting started
related: variables, matrices, functions, control-flow, repl
---

# Language Basics

MathTool follows a MATLAB-like expression style. Statements can end with a semicolon to suppress the displayed result.

## Expressions

```mathtool
x = 2 + 3 * 4;
y = sin(pi / 2)
```

## Comments

Use `%` for comments.

```mathtool
% Compute a sampled sine wave
x = linspace(0, 2*pi, 100);
y = sin(x);
```

## Command-style calls

Some commands can be typed without parentheses:

```mathtool
help plot
lookfor matrix
doc matrices
```

## Structs

Structs use MATLAB-style dot assignment and dot access:

```mathtool
student.name = 'Alice';
student.id = 12345;
student.grades = [95 88 91];

user.address.city = 'Boston';
city = user.address.city;

person = struct('name', 'Bob', 'age', 30);
```

Assigning a dotted field creates missing structs along the path.
Reading a missing field raises an error such as
`Reference to non-existent field 'city'`. One-dimensional struct arrays
are supported for field assignment and access:

```mathtool
students(1).name = 'Alice';
students(2).name = 'Bob';
first = students(1).name;
```

Related: [Variables](topic:variables), [Matrices](topic:matrices), [Control Flow](topic:control-flow).
