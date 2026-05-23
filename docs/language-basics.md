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

Related: [Variables](topic:variables), [Matrices](topic:matrices), [Control Flow](topic:control-flow).
