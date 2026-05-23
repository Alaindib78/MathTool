---
id: functions
title: Functions
category: Functions
summary: Define reusable `.m` functions and document them with MATLAB-style help comments.
keywords: function, user function, m file, help comments, documentation
aliases: user functions, function files
related: language-basics, workspace, help, lookfor
---

# Functions

Function files start with a `function` declaration. Help text is read from the comment block immediately after the declaration.

```mathtool
function y = squareNumber(x)
% SQUARENUMBER Squares the input value.
%
%   y = SQUARENUMBER(x) returns x squared.
%
%   Example:
%       y = squareNumber(5)
%
%   See also sqrt
    y = x ^ 2;
end
```

Save the file as `squareNumber.m` on the current folder or search path. The Help browser indexes the comment block automatically.

Related: [help](topic:help), [lookfor](topic:lookfor), [Workspace](topic:workspace).
