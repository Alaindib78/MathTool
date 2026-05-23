---
id: debugging
title: Debugging
category: Debugging
summary: Use breakpoints, debug execution, stepping, and workspace inspection to understand code.
keywords: debug, breakpoints, step, continue, workspace, diagnostics
aliases: debugger, breakpoints
related: ide-features, workspace, control-flow
---

# Debugging

MathTool includes breakpoint-driven debugging in the editor. Add a breakpoint next to a line, start debugging, then step through execution while watching the workspace.

## Common workflow

1. Open a script or function.
2. Add breakpoints on lines you want to inspect.
3. Start debugging.
4. Use Step or Continue.
5. Inspect variables in the Workspace panel.

```mathtool
x = linspace(0, 1, 5);
y = x.^2;
disp(y);
```

Related: [Workspace](topic:workspace), [Control Flow](topic:control-flow), [IDE Features](topic:ide-features).
