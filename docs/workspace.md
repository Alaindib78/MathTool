---
id: workspace
title: Workspace
category: Workspace
summary: Inspect variables, current folder state, and runtime paths from the IDE.
keywords: workspace, variables, current folder, path, search path, variable editor
aliases: variable panel, current folder
related: variables, repl, functions
---

# Workspace

The Workspace panel shows variables created by scripts and REPL commands. Double-click a variable to inspect it in a variable editor.

## Useful commands

```mathtool
who
cwd
clear
```

## Function paths

MathTool searches built-ins first, then local functions, the core library, the current folder, and external paths. The Path Manager helps inspect and edit that order.

Related: [Variables](topic:variables), [Functions](topic:functions), [REPL](topic:repl).
