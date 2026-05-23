---
id: control-flow
title: Control Flow
category: Control Flow
summary: Branch and repeat work with if, for, while, break, continue, and return.
keywords: if, elseif, else, for, while, break, continue, return, loops
aliases: loops, branching
related: language-basics, debugging
---

# Control Flow

Use `if`, `elseif`, and `else` to branch.

```mathtool
x = 7;
if x > 0
    disp('positive')
else
    disp('non-positive')
end
```

Use loops for repeated work.

```mathtool
total = 0;
for k = 1:5
    total = total + k;
end
```

`break` exits a loop, `continue` skips to the next iteration, and `return` exits a function.
