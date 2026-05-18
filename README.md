# MathTool

MathTool is a small MATLAB-like interpreter written in Python. It includes a lexer, parser, semantic analyzer, runtime interpreter, standard library functions, plotting support, a REPL, and a PySide6 desktop GUI.

## Features

- Numeric expressions with operator precedence
- Variables and assignment
- Strings and comments
- Boolean and comparison operators, including `&&`, `||`, `~`, `==`, and `~=`
- `if`, `elseif`, `else`, `for`, and `while`
- User-defined functions, including recursive calls
- Explicit `return` statements and MATLAB-style implicit return variables
- Ranges such as `1:5` and `0:0.1:1`
- Vector and matrix literals
- Matrix multiplication with `*`
- Element-wise operators: `.*`, `./`, `.^` (`.*` requires same-size array operands)
- Matrix transpose with `'`
- One-based indexing such as `M(2, 1)`
- MATLAB-style complex numbers with `i`, `j`, `1i`, `complex`, `sqrt`, `exp`, `angle`, `conj`, `real`, `imag`, and `isreal`
- Symbolic variables with `syms`, `sym`, `class`, and `ans`
- Built-ins including `sin`, `cos`, `sqrt`, `exp`, `complex`, `angle`, `conj`, `real`, `imag`, `isreal`, `zeros`, `ones`, `length`, `plot`, `title`, `xlabel`, `ylabel`, and `grid`
- Desktop GUI with editor tabs, output console, command window, workspace table, and basic debugging controls

## Project Structure

```text
core/
  ast/             AST node definitions
  debugger/        Debugger hooks and call control
  errors/          MathTool error types
  interpreter/     Runtime evaluator
  lexer/           Tokenizer
  parser/          Parser
  plotting/        Matplotlib plotting bridge
  runtime/         REPL, context, functions, and call stack
  semantic/        Semantic analyzer and symbol table
  stdlib/          Built-in functions
gui/               PySide6 desktop application
examples/          Example .m scripts
tests/             Pytest test suites
main.py            CLI REPL entrypoint
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
exit
```

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

print(pgcd(55, 21));
```

Matrix example:

```matlab
M1 = [1 -1;
      2 2];

M2 = [1; -1];

TM1 = M1' * M2;

print(TM1);
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
- Built-in `print` and `println` write to the GUI console when an output callback is configured.
- Plotting uses Matplotlib through `core.plotting.engine.PlotEngine`.
- The GUI executes scripts on a worker thread and routes output/workspace updates back to the Qt main thread through signals.
