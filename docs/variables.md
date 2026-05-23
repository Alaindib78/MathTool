---
id: variables
title: Variables
category: Variables
summary: Create, inspect, reuse, and clear values in the active workspace.
keywords: assignment, workspace, who, clear, constants, variables
aliases: assignment, workspace variables
related: workspace, language-basics, repl
---

# Variables

Assign values with `=`. Variable names are case-sensitive and can store numbers, strings, logical values, arrays, matrices, symbolic expressions, or structs.

```mathtool
radius = 3;
area = pi * radius^2;
label = 'disk';
```

## Inspect variables

```mathtool
who
disp(area)
```

## Reserved constants

| Name | Value |
| --- | --- |
| `pi` | Circle constant |
| `e` | Euler constant |
| `true` | Logical true |
| `false` | Logical false |

See also [Workspace](topic:workspace), [REPL](topic:repl), [disp](topic:disp).
