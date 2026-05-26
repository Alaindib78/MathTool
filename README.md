# MathTool

MathTool is a small MATLAB-like interpreter written in Python. It includes a lexer, parser, semantic analyzer, runtime interpreter, standard library functions, plotting support, a REPL, and a PySide6 desktop GUI.

## Features

- Numeric expressions with operator precedence
- Variables and assignment
- Strings and comments
- Boolean and comparison operators, including `&&`, `||`, `~`, `==`, and `~=`
- `if`, `elseif`, `else`, `for`, and `while`, with `break` and `continue`
- User-defined functions, including recursive calls
- Bare and value-returning `return` statements plus MATLAB-style implicit return variables
- Ranges such as `1:5` and `0:0.1:1`
- Vector and matrix literals
- Matrix multiplication with `*`
- Element-wise operators: `.*`, `./`, `.^` (`.*` requires same-size array operands)
- Matrix transpose with `'`
- One-based indexing such as `M(2, 1)`
- MATLAB-style structs with dot assignment/access, nested fields, `struct(...)`, and one-dimensional struct arrays such as `students(1).name`
- MATLAB-style complex numbers with `i`, `j`, `1i`, `complex`, `sqrt`, `exp`, `angle`, `conj`, `real`, `imag`, and `isreal`
- Symbolic variables with `syms`, `sym`, `class`, and `ans`
- Symbolic equation solving with `solve`, `symvar`, and `Name=Value` options such as `Real=true`
- Built-ins including console utilities (`disp`, `fprintf`, `warning`, `error`), engineering math, array construction/shape helpers, reductions/statistics, linear algebra, FFT, polynomial utilities, interpolation/integration helpers, plotting, symbolic math, and complex-number utilities
- MATLAB-style function help comments with `help`, `help eig`, `help("eig")`, and `lookfor keyword`
- Desktop GUI with editor tabs, output console, command window, workspace table, and basic debugging controls

## Project Structure

```text
core/
  ast/             AST node definitions
  debugger/        Debugger hooks and call control
  errors/          MathTool error types
  interpreter/     Runtime evaluator
  library/         Optional .m library functions loaded for every runtime
  lexer/           Tokenizer
  parser/          Parser
  plotting/        Matplotlib plotting bridge
  runtime/         REPL, context, functions, and call stack
  semantic/        Semantic analyzer and symbol table
  stdlib/          Built-in functions
api/               FastAPI REST backend
gui/               PySide6 desktop application
examples/          Example .m scripts
tests/             Pytest test suites
main.py            CLI REPL entrypoint
run_api.py         API backend entrypoint
run_gui.py         GUI entrypoint
```

## Requirements

- Python 3.14 or newer
- Dependencies listed in `requirements.txt`

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

For running tests, install pytest if it is not already available:

```powershell
python -m pip install pytest
```

## Run The REPL

```powershell
python main.py
```

The REPL supports normal MathTool statements and simple commands:

```text
who
clear
help
help eig
lookfor matrix
cwd
exit
```

If `script_1.m` is a script in the current working directory, type
`script_1` in the REPL or GUI command window to run it.

Function files can include MATLAB-style help blocks immediately after
the function definition:

```matlab
function y = squareNumber(x)
% SQUARENUMBER Squares the input value.
%
%   y = SQUARENUMBER(x) returns x squared.
%
%   Example:
%       y = squareNumber(5)
%
%   See also sqrt, power
    y = x ^ 2;
end
```

The GUI Documentation panel indexes built-ins and documented functions
on the current function path, supports search, and renders see-also
links.

## Run The GUI

```powershell
python run_gui.py
```

The GUI provides:

- Multi-tab code editor
- Syntax highlighting
- Run button
- Output console
- Command window
- Workspace variable table
- Variable inspection
- Basic breakpoint and stepping controls

## Run The API

```powershell
python run_api.py
```

The API starts on `http://127.0.0.1:8000` by default. It provides
session-based REST endpoints for executing MathTool code, reading the
workspace, managing the current working directory/search path, and
querying help text. Interactive API docs are available at
`http://127.0.0.1:8000/docs` when the server is running.
The first web HMI is served from `http://127.0.0.1:8000/`.

Basic flow:

```text
POST /sessions
POST /sessions/{session_id}/execute
POST /sessions/{session_id}/command
GET  /sessions/{session_id}/workspace
POST /sessions/{session_id}/workspace/clear
```

## Example Script

```matlab
function c = pgcd(a, b)
    if a == b
        c = a
    elseif a > b
        c = pgcd(a - b, b);
    else
        c = pgcd(a, b - a);
    end
end

disp(pgcd(55, 21));
```

Matrix example:

```matlab
M1 = [1 -1;
      2 2];

M2 = [1; -1];

TM1 = M1' * M2;

disp(TM1);
```

Symbolic example:

```matlab
syms x
x

x = 1 / 33;
class(x);

x = sym('1/33');
class(x);
```

Solve example:

```matlab
syms a b c x
eqn = a*x^2 + b*x + c == 0;

S = solve(eqn);
Sa = solve(eqn, a);
real_roots = solve(x^2 + 1 == 0, x, Real=true);

syms u v
eqns = [2*u + v == 0, u - v == 1];
Y = solve(eqns, [u v]);
```

Struct example:

```matlab
student.name = 'Alice';
student.id = 12345;
student.grades = [95 88 91];

user.address.city = 'Boston';
city = user.address.city;

person = struct('name', 'Bob', 'age', 30);
students(1).name = 'Alice';
students(2).name = 'Bob';
```

Missing field reads raise an error such as
`Reference to non-existent field 'city'`. Dot assignment auto-creates
missing intermediate structs, while dot access does not. Struct arrays
currently support one-dimensional indexing for field assignment/access.

Complex number example:

```matlab
z = 1 + 2i;

x = [1:4]';
y = [8:-2:2]';
column = x + 1i*y;

r = 4;
theta = pi/4;
polar = r*exp(1i*theta);

phase = angle(z);
mirror = conj(z);
parts = [real(z) imag(z)];
```

`isreal` follows MATLAB's storage-oriented behavior:

```matlab
isreal([1 2 3]);
isreal(complex(1, 0));
```

Plotting example:

```matlab
t = 0:0.1:2*pi;
y = sin(t);

plot(t, y);
title("sine wave");
xlabel("time (s)");
ylabel("V (volts)");
grid(true);
```

More examples are available in `examples/`.

## Run Tests

```powershell
python -m pytest
```

The active pytest configuration runs tests from the `tests/` directory.

## Development Notes

- Constants `pi`, `e`, `true`, and `false` are loaded into every runtime context. The names `i` and `j` resolve to the imaginary unit unless the user assigns over them.
- Constants are treated as immutable by the semantic analyzer.
- `ans` stores the result of the last expression that is not assigned to a named variable.
- Built-in `disp`, `fprintf`, `warning`, and `error` write to the GUI console when an output callback is configured.
- Plotting uses Matplotlib through `core.plotting.engine.PlotEngine`.
- The GUI executes scripts on a worker thread and routes output/workspace updates back to the Qt main thread through signals.
- `.m` function files placed in `core/library/` or any of its subdirectories are available to the CLI, GUI, and API. Built-ins still have highest priority, then same-file/local functions, then `core/library/`, then the current working directory and configured external search paths.
