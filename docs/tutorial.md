---
id: tutorial
title: Tutorial
category: Getting Started
summary: A step-by-step, example-heavy tour of MathTool's language, IDE, plotting, functions, workspace, debugging, help system, and API.
keywords: tutorial, getting started, guide, examples, matlab, ide, plotting, matrices, functions, symbolic, api
aliases: getting started, user guide, full tutorial
related: language-basics, variables, matrices, functions, plotting-guide, workspace, debugging, repl, help-system
---

# MathTool Tutorial

This tutorial walks through MathTool as a MATLAB-like scientific IDE.
It covers the language, the desktop interface, plotting, the command
window, scripts, functions, matrices, structs, symbolic math, help,
debugging, and the API.

The examples are written in MathTool syntax. You can run them from:

- the script editor with the Run button
- the Command Window, one command at a time
- the CLI REPL started with `python main.py`
- the API by sending the source to an execution endpoint

## 1. Start MathTool

### Desktop GUI

From the project root:

```powershell
python run_gui.py
```

The GUI contains:

- a multi-tab editor
- a command window
- an output console
- a workspace table
- a current folder browser
- a path manager
- an integrated help browser
- embedded plotting
- debugging controls

### CLI REPL

```powershell
python main.py
```

Useful REPL commands:

```mathtool
help
help plot
lookfor matrix
doc matrices
who
cwd
clear
exit
```

### API Backend

```powershell
python run_api.py
```

The API defaults to `http://127.0.0.1:8000`. Interactive FastAPI docs
are available at:

```text
http://127.0.0.1:8000/docs
```

The web HMI is served from:

```text
http://127.0.0.1:8000/
```

## 2. Your First Calculation

Type this in the Command Window:

```mathtool
2 + 3 * 4
```

MathTool uses normal operator precedence, so the result is `14`.

Assign the result:

```mathtool
A = 2 + 3 * 4;
B = A / 2;
B
```

The semicolon suppresses console display for that statement. The
workspace still stores the values.

The variable `ans` stores the result of the last unassigned expression:

```mathtool
sqrt(81)
ans + 1
```

## 3. Variables And Constants

Create variables with assignment:

```mathtool
radius = 3;
area = pi * radius ^ 2;
```

Built-in constants:

```mathtool
pi
e
true
false
```

`pi`, `e`, `true`, and `false` are immutable. Assigning to them raises
a semantic error.

The imaginary units `i` and `j` default to `1i`, unless you assign over
them:

```mathtool
z1 = 1 + 2i;
z2 = 3 - 4j;
```

Use `who` to list workspace variables:

```mathtool
who
```

Use `clear` to reset user variables:

```mathtool
clear
```

## 4. Comments, Strings, And Output

Use `%` for comments:

```mathtool
% Compute kinetic energy
m = 2.5;
v = 12;
E = 0.5 * m * v ^ 2;
```

Strings can use double quotes or single quotes where the parser can
distinguish them from transpose:

```mathtool
message1 = "Hello MathTool";
message2 = 'Symbol name';
```

Display values:

```mathtool
disp("Result:");
disp(E);
```

Formatted output:

```mathtool
fprintf("mass = %.2f kg\n", m);
fprintf("energy = %.1f J\n", E);
```

Warnings and errors:

```mathtool
warning("Temperature %.1f is high", 91.5);
error("File %s not found", "data.csv");
```

## 5. Numeric Literals

### Decimal Numbers

```mathtool
a = 42;
b = 3.14159;
c = -12.5;
```

### Complex Literals

```mathtool
z = 1 + 2i;
w = 3 - 4j;
unit = i;
```

Complex helpers:

```mathtool
phase = angle(z);
mirror = conj(z);
realPart = real(z);
imagPart = imag(z);
isPlainReal = isreal([1 2 3]);
```

### Hexadecimal And Binary Integer Literals

MathTool supports MATLAB-style prefixed integer literals:

```mathtool
A = 0x2A;
B = 0X2A;
C = 0b101010;
D = 0B101010;

disp([A B C D]);  % all are 42
```

Lowercase hex digits are accepted:

```mathtool
value = 0xff;  % 255
```

Typed suffixes are supported:

```mathtool
u = 0xFFu8;
s = 0xFFs8;

class(u);  % uint8
class(s);  % int8
```

Signed suffixes use two's-complement interpretation:

```mathtool
a = 0xFFs8;        % -1
b = 0xFFFFs16;     % -1
c = 0xFFFFFFFFs32; % -1
```

Conversion helpers:

```mathtool
dec2hex(255);      % "FF"
dec2bin(16);       % "10000"
hex2dec("FF");     % 255
bin2dec("1010");   % 10
```

Bitwise helpers:

```mathtool
a = bitand(0b1100, 0b1010);   % 8
b = bitor(0b1100, 0b1010);    % 14
c = bitxor(0b1100, 0b1010);   % 6
d = bitshift(0b0011, 2);      % 12
e = bitget(0b1010, 2);        % 1
f = bitset(0b1000, 2, true);  % 10
```

## 6. Arithmetic Operators

Scalar arithmetic:

```mathtool
a = 10 + 3;
b = 10 - 3;
c = 10 * 3;
d = 10 / 3;
e = 10 ^ 3;
```

Unary operators:

```mathtool
x = -5;
y = +10;
```

Scalar arithmetic also applies across numeric vectors and range values:

```mathtool
t = 0:0.1:2*pi;
y = sin(2*t);
z = 1 - t;
q = t ^ 2;
```

Element-wise operators:

```mathtool
A = [1 2 3];
B = [4 5 6];

C = A .* B;
D = B ./ A;
E = A .^ 2;
```

Matrix multiplication uses `*`:

```mathtool
M = [1 2; 3 4];
N = [5 6; 7 8];
P = M * N;
```

## 7. Logical Expressions

Comparisons:

```mathtool
a = 5;
b = 3;

isGreater = a > b;
isLess = a < b;
isEqual = a == 5;
isDifferent = a ~= b;
```

Logical operators:

```mathtool
ok = (a > 1) && (b < 10);
either = (a < 1) || (b < 10);
notLess = ~(a < b);
```

Logical operations work on arrays too:

```mathtool
A = [1 2 3; 4 5 6; 7 8 9];
mask = A > 5;
between = A > 2 & A < 8;
```

## 8. Ranges

Ranges use MATLAB-style colon syntax:

```mathtool
r1 = 1:5;
r2 = 0:0.25:1;
r3 = 10:-2:2;
```

Ranges are useful in loops, plots, and indexing:

```mathtool
x = 0:0.1:2*pi;
y = sin(x);

plot(x, y);
```

Note: floating-point range endpoints follow normal floating-point
precision limits. If you need exactly `n` samples, use `linspace`.

```mathtool
x = linspace(0, 1, 11);
```

## 9. Vectors And Matrices

Create row vectors:

```mathtool
v = [1 2 3 4];
w = [1, 2, 3, 4];
```

Create column vectors:

```mathtool
c = [1; 2; 3; 4];
```

Create matrices:

```mathtool
A = [1 2 3;
     4 5 6;
     7 8 9];
```

Mix literals:

```mathtool
B = [0x1 0x2;
     0b11 0b100];
```

Construction helpers:

```mathtool
Z = zeros(3);
R = zeros(2, 4);
O = ones(2, 3);
I = eye(4);
T = true(2, 3);
F = false(2, 3);
```

Shape and size:

```mathtool
dims = size(A);
rows = size(A, 1);
cols = size(A, 2);
n = numel(A);
rankCount = ndims(A);
isEmpty = isempty([]);
```

Reshape and diagonals:

```mathtool
B = reshape(1:6, 2, 3);
flat = flatten(A);
D = diag([1 2 3]);
mainDiag = diag(A);
lower = tril(A);
upper = triu(A);
```

## 10. Indexing

MathTool uses 1-based indexing.

```mathtool
A = [1 2 3;
     4 5 6;
     7 8 9];

x = A(2, 3);  % 6
```

Select rows, columns, and blocks:

```mathtool
row2 = A(2, :);
col3 = A(:, 3);
block = A(1:2, 2:3);
```

Use `end`:

```mathtool
last = A(end, end);
lastRow = A(end, :);
middleRows = A(1:end-1, :);
```

Single-subscript indexing uses column-major order:

```mathtool
first = A(1);
third = A(3);
fifth = A(5);
picked = A([1 5 9]);
```

Flatten with `:`

```mathtool
columnMajor = A(:);
```

Logical indexing:

```mathtool
mask = A > 5;
selected = A(mask);
```

Indexed assignment:

```mathtool
A(1, 1) = 100;
A(2, :) = [10 11 12];
A(1:2, 1:2) = 99;
A(A > 5 & A < 9) = 0;
```

## 11. Matrix And Array Math

Element-wise vector operations:

```mathtool
x = [1 2 3 4];
y = x .^ 2;
z = sqrt(y);
```

Matrix multiplication:

```mathtool
A = [1 2; 3 4];
B = [5 6; 7 8];
C = A * B;
```

Linear algebra:

```mathtool
A = [1 2; 3 4];
b = [5; 11];

d = det(A);
Ainv = inv(A);
x = linsolve(A, b);
p = pinv(A);
r = rank(A);
c = cond(A);
tr = trace(A);
```

Factorizations:

```mathtool
E = eig(A);
eigenvalues = E.values;
eigenvectors = E.vectors;

S = svd(A);
Q = qr(A);
```

Vector operations:

```mathtool
dotValue = dot([1 2 3], [4 5 6]);
crossValue = cross([1 0 0], [0 1 0]);
normValue = norm([3 4]);
```

## 12. Built-In Math Functions

Trigonometry:

```mathtool
x = pi / 4;
s = sin(x);
c = cos(x);
t = tan(x);
a = atan2(1, 1);
```

Inverse and hyperbolic functions:

```mathtool
asin(1);
acos(0);
atan(1);
sinh(1);
cosh(1);
tanh(1);
asinh(1);
acosh(2);
atanh(0.5);
```

Logarithms and exponentials:

```mathtool
log(e);
log10(1000);
log2(8);
exp(1);
expm1(0.001);
```

Rounding and clipping:

```mathtool
floor(3.9);
ceil(3.1);
round(3.14159, 2);
fix(-3.9);
clip([-2 0 5], 0, 3);
sign([-5 0 7]);
```

Angle conversion:

```mathtool
radians = deg2rad(180);
degrees = rad2deg(pi);
```

## 13. Reductions And Statistics

```mathtool
A = [1 2 3; 4 5 6];

s = sum(A);
p = prod(A);
m = mean(A);
med = median(A);
mx = max(A);
mn = min(A);
sd = std(A);
variance = var(A);
p50 = percentile(A, 50);
```

Dimension arguments are 1-based where supported:

```mathtool
sumRows = sum(A, 2);
sumCols = sum(A, 1);
meanCols = mean(A, 1);
```

Logical reductions:

```mathtool
any([0 0 1]);
all([1 1 1]);
```

Numeric tests:

```mathtool
values = [1 2 3];
isnan(values);
isinf(values);
isfinite(values);
isclose(1, 1 + 1e-9);
allclose([1 2], [1 2.000000001]);
```

## 14. Sorting, Finding, And Set-Like Helpers

```mathtool
values = [3 1 3 2];

sorted = sort(values);
uniqueValues = unique(values);
positions = find(values > 2);
```

`find` returns 1-based linear indices.

## 15. Numerical Calculus And Signal Helpers

Differences and gradients:

```mathtool
y = [1 4 9 16];
d = diff(y);
g = gradient(y);
```

Cumulative operations:

```mathtool
x = [1 2 3 4];
cs = cumsum(x);
cp = cumprod(x);
```

Integration and interpolation:

```mathtool
x = [0 1 2];
y = [0 1 0];
area = trapz(x, y);
mid = interp1(x, y, 0.5);
```

FFT helpers:

```mathtool
signal = [1 0 0 0];
F = fft(signal);
roundTrip = ifft(F);
shifted = fftshift(F);
unshifted = ifftshift(shifted);
freq = fftfreq(8, 0.1);
```

Polynomial helpers:

```mathtool
r = roots([1 0 -1]);
v = polyval([1 0 -1], 3);
coeff = polyfit([0 1 2], [1 2 5], 2);
cv = conv([1 2], [3 4]);
```

## 16. Random Numbers

Create reproducible random numbers:

```mathtool
rng(123);
A = rand(2, 2);

rng(123);
B = rand(2, 2);

same = allclose(A, B);
```

Other random helpers:

```mathtool
normal = randn(3, 1);
integer = randi(10);
matrix = randi(10, 3, 3);
```

## 17. Control Flow

### If, ElseIf, Else

```mathtool
score = 83;

if score >= 90
    grade = "A";
elseif score >= 80
    grade = "B";
elseif score >= 70
    grade = "C";
else
    grade = "Needs review";
end
```

### For Loops

```mathtool
total = 0;

for k = 1:10
    total = total + k;
end
```

### While Loops

```mathtool
n = 0;
value = 1;

while value < 100
    n = n + 1;
    value = value * 2;
end
```

### Break And Continue

```mathtool
total = 0;

for k = 1:10
    if k == 3
        continue;
    end

    if k > 7
        break;
    end

    total = total + k;
end
```

## 18. User Functions

Define functions in scripts or `.m` files:

```mathtool
function y = square(x)
    y = x ^ 2;
end

answer = square(5);
```

Multiple outputs:

```mathtool
function [m, s] = stats(x)
    n = length(x);
    m = sum(x) / n;
    s = sqrt(sum((x - m) .^ 2) / n);
end

[average, spread] = stats([1 2 3 4]);
```

Early return with a value:

```mathtool
function y = firstPositive(x)
    if x > 0
        return x;
    end

    y = 0;
end
```

Bare return:

```mathtool
function y = clampPositive(x)
    y = 0;

    if x > 0
        y = x;
        return;
    end
end
```

Function files should use the same name as the function:

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

Save this as `squareNumber.m` in the current folder or on the search
path. The help browser indexes the comment block.

## 19. Function Lookup And Paths

MathTool resolves functions in this order:

1. built-ins
2. same-file or local functions
3. functions in `core/library`
4. current working directory
5. configured external search paths

Useful commands:

```mathtool
cwd
who
help squareNumber
lookfor square
```

In the GUI, use the current folder browser and path manager to inspect
and adjust function paths.

## 20. Structs

Create structs by assigning fields:

```mathtool
student.name = "Alice";
student.id = 12345;
student.grades = [95 88 91];

disp(student.name);
```

Nested structs:

```mathtool
user.name = "Bob";
user.address.city = "Boston";
user.address.zip = 2108;

city = user.address.city;
```

Create structs with `struct`:

```mathtool
person = struct("name", "Carol", "age", 30);
empty = struct();
empty.x = 5;
```

Struct arrays:

```mathtool
students(1).name = "Alice";
students(1).grade = 95;
students(2).name = "Bob";
students(2).grade = 88;

firstName = students(1).name;
secondGrade = students(2).grade;
```

Dot assignment creates missing intermediate structs. Dot access does
not create missing fields; reading a missing field raises an error.

## 21. Symbolic Math

Declare symbolic variables:

```mathtool
syms x y
expr = x ^ 2 + 2*x + 1;
```

Create exact symbolic values:

```mathtool
exact = sym("1/33");
kind = class(exact);
```

Simplify, expand, collect, and factor:

```mathtool
syms x
expr = (x + 1) ^ 2;

expanded = expand(expr);
simplified = simplify(expanded - (x^2 + 2*x + 1));
collected = collect(expanded, x);
factored = factor(x^2 - 1);
```

Substitute values:

```mathtool
value = subs(x^2 + 1, x, 3);
```

Return coefficients:

```mathtool
c = coeffs(x^2 + 2*x + 1, x);
```

Solve one equation:

```mathtool
syms x
roots = solve(x^2 - 1 == 0, x);
```

Solve a symbolic quadratic:

```mathtool
syms a b c x
eqn = a*x^2 + b*x + c == 0;

S = solve(eqn);
Sa = solve(eqn, a);
```

Solve a system:

```mathtool
syms u v
eqns = [2*u + v == 0, u - v == 1];
Y = solve(eqns, [u v]);
```

Filter real solutions:

```mathtool
realRoots = solve(x^2 + 1 == 0, x, Real=true);
```

Find symbolic variables:

```mathtool
vars = symvar(eqns);
```

## 22. Plotting

### Simple Plot

```mathtool
t = 0:0.1:2*pi;
y = sin(2*t);

plot(t, y);
title("Sine wave");
xlabel("time");
ylabel("amplitude");
grid on;
```

### Implicit X

If you pass one vector, MathTool plots it against `1:length(Y)`:

```mathtool
y = [4 1 3 6];
plot(y);
```

For a matrix, each column becomes a separate line:

```mathtool
Y = [1 3 5;
     2 4 6;
     3 5 7;
     4 6 8];

plot(Y);
```

### Multiple Lines

```mathtool
x = 0:0.1:2*pi;
y1 = sin(x);
y2 = cos(x);

plot(x, y1, x, y2);
```

### LineSpec Strings

Supported line styles:

```text
-    solid
--   dashed
:    dotted
-.   dash-dot
```

Supported markers:

```text
o + * . x s d ^ v > < p h
```

Supported colors:

```text
r g b c m y k w
```

Examples:

```mathtool
plot(x, y1, "r--");
plot(x, y1, "bo");
plot(x, y1, "g-*");
plot(y1, ":");
plot(x, y1, "r", x, y2, "b--o");
```

### Name-Value Properties

```mathtool
plot(x, y1, "LineWidth", 2);
plot(x, y1, "Color", [0 0.7 0.9]);
plot(x, y1, "--gs", "LineWidth", 2, "MarkerSize", 10);
```

Supported properties include:

- `Color`
- `LineStyle`
- `LineWidth`
- `Marker`
- `MarkerSize`
- `MarkerEdgeColor`
- `MarkerFaceColor`
- `MarkerIndices`

Examples:

```mathtool
plot(x, y1, "Color", "red");
plot(x, y1, "Marker", "o", "MarkerSize", 8);
plot(x, y1, "MarkerFaceColor", [0.5 0.5 0.5]);
plot(x, y1, "MarkerIndices", 1:5:length(y1));
```

### Hold Behavior

With hold off, each `plot` call clears the active axes before drawing.

```mathtool
figure(1);
plot(x, y1);
plot(x, y2);  % replaces y1
```

Use hold on to add lines:

```mathtool
figure(1);
plot(x, y1, "r");
hold on;
plot(x, y2, "b--");
hold off;
```

### Multiple Figures

```mathtool
figure(1);
plot(x, sin(x));
title("Sine");

figure(2);
plot(x, cos(x));
title("Cosine");

figure(1);
hold on;
plot(x, sin(2*x), "r--");
hold off;
```

Clean up:

```mathtool
close;
close(2);
close all;
```

### Control-System Plots

```mathtool
num = [1];
den = [1 1];
w = [0.1 1 10];

bode(num, den, w);
nyquist(num, den, [0 1]);
```

## 23. Display Formatting

Formatting changes output display only. Stored values do not change.

```mathtool
x = pi;

format long
disp(x);

format short
disp(x);

format compact
disp(x);

format loose
```

Function form:

```mathtool
format("shortE");
settings = formatsettings();
```

Supported styles include:

- `short`
- `long`
- `shortE`
- `longE`
- `shortG`
- `longG`
- `shortEng`
- `longEng`
- `bank`
- `rat`
- `hex`
- `+`
- `compact`
- `loose`
- `default`

## 24. Help And Documentation

Console help:

```mathtool
help
help plot
help("linspace")
```

Keyword search:

```mathtool
lookfor eigen
lookfor("matrix")
```

Open a help topic in the integrated browser:

```mathtool
doc plot
doc matrices
doc shortcuts
```

Function files can provide help comments immediately after the function
declaration:

```mathtool
function y = squareNumber(x)
% SQUARENUMBER Squares the input value.
%
%   y = SQUARENUMBER(x) returns x squared.
%
%   Example:
%       squareNumber(5)
%
%   See also sqrt
    y = x ^ 2;
end
```

## 25. Workspace And Variable Inspection

The Workspace panel lists variables created by scripts and REPL
commands.

Try:

```mathtool
A = [1 2 3; 4 5 6];
z = 1 + 2i;
student.name = "Alice";
who
```

In the GUI:

1. Run the script.
2. Inspect the Workspace panel.
3. Double-click a variable to open it in the variable editor.
4. Use `clear` to reset user variables.

Current folder and path:

```mathtool
cwd
```

Use the path manager for additional folders containing `.m` function
files.

## 26. Debugging

Suggested workflow:

1. Open a script in the editor.
2. Add a breakpoint next to a line.
3. Start debugging.
4. Use Step and Continue.
5. Watch variables change in the Workspace panel.

Example script:

```mathtool
total = 0;

for k = 1:5
    square = k ^ 2;
    total = total + square;
end

disp(total);
```

Good breakpoint locations:

- `square = k ^ 2;`
- `total = total + square;`
- `disp(total);`

Debugging is most useful when you combine it with the Workspace panel
and the Output console.

## 27. Command Window Workflows

Use the Command Window for small experiments:

```mathtool
x = linspace(0, 1, 5)
y = x.^2
plot(x, y, "ro-")
```

Use command history with the Up and Down keys.

Run a script by name if it is in the current folder or search path:

```mathtool
my_script
```

## 28. Script Examples

The `examples/` folder contains runnable scripts. Good starting points:

```text
examples/matlab_style_plot_example.m
examples/hex_binary_integer_literals_example.m
examples/sudoku_solver_example.m
examples/figure_close_example.m
examples/Complet_test.m
```

Open one in the editor and run it.

## 29. API Tutorial

Start the API:

```powershell
python run_api.py
```

Create a session:

```http
POST /sessions
```

Execute code:

```http
POST /sessions/{session_id}/execute
Content-Type: application/json

{
  "source": "A = [1 2; 3 4];"
}
```

Run an interactive command:

```http
POST /sessions/{session_id}/command
Content-Type: application/json

{
  "source": "who"
}
```

Read the workspace:

```http
GET /sessions/{session_id}/workspace
```

Clear workspace:

```http
POST /sessions/{session_id}/workspace/clear
```

Manage current working directory and paths:

```http
PUT /sessions/{session_id}/cwd
POST /sessions/{session_id}/paths
```

Search help:

```http
GET /sessions/{session_id}/help/search?q=plot
GET /sessions/{session_id}/help/topic/plot
GET /sessions/{session_id}/help/index
GET /sessions/{session_id}/help/categories
GET /sessions/{session_id}/help/examples
```

Plot results are serialized when the session uses the recording plot
engine, which is what the API uses for web-friendly plot responses.

## 30. A Complete Mini Project

This example combines ranges, vector math, plotting, functions, structs,
formatted output, and workspace inspection.

```mathtool
% Damped oscillator demo

function y = dampedSine(t, frequency, decay)
    y = exp(-decay .* t) .* sin(2*pi*frequency .* t);
end

settings.frequency = 2;
settings.decay = 0.4;
settings.samples = 400;

t = linspace(0, 5, settings.samples);
y = dampedSine(t, settings.frequency, settings.decay);

energy = trapz(t, y .* y);

figure(1);
plot(t, y, "b-", "LineWidth", 2);
title("Damped sine wave");
xlabel("time");
ylabel("amplitude");
grid on;

fprintf("Energy estimate: %.4f\n", energy);
who
```

Try adding another trace:

```mathtool
hold on;
plot(t, exp(-settings.decay .* t), "r--");
plot(t, -exp(-settings.decay .* t), "r--");
hold off;
```

## 31. Common Errors And Fixes

### Undefined variable

```mathtool
y = missingName + 1;
```

Fix: assign the variable first, or check spelling.

### Undefined function

```mathtool
result = myFunction(1);
```

Fix: define `myFunction`, put `myFunction.m` on the current folder or
path, or check the function name.

### Matrix dimension mismatch

```mathtool
A = [1 2 3];
B = [4 5];
C = A .* B;
```

Fix: use same-size arrays or compatible scalar expansion where
supported.

### Division by zero

```mathtool
x = 5 / 0;
```

Fix: check denominators before dividing.

### Index out of bounds

```mathtool
A = [1 2 3];
x = A(4);
```

Fix: remember indices are 1-based and must be within the array size.

### Missing struct field

```mathtool
s.name = "Alice";
age = s.age;
```

Fix: assign `s.age` before reading it.

### Invalid plot data

```mathtool
plot("not numeric");
```

Fix: pass numeric scalars, vectors, or matrices.

### Invalid LineSpec

```mathtool
plot([1 2 3], "rq--");
```

Fix: use valid style, marker, and color symbols such as `"r--"`,
`"bo"`, or `"g-*"`.

## 32. MATLAB Compatibility Notes

MathTool is MATLAB-like, not a full MATLAB clone. Important limits:

- Full graphics object handles are not implemented.
- Table and timetable plotting are not implemented.
- Advanced axes targeting such as `plot(ax, ...)` is not implemented.
- Struct arrays are focused on one-dimensional field access patterns.
- Most numeric arrays are backed by Python and NumPy behavior.
- Symbolic math uses SymPy underneath and may format results differently
  from MATLAB.
- Some MATLAB toolbox functions are not present.

When in doubt, use:

```mathtool
help functionName
doc topicName
lookfor keyword
```

## 33. Practice Exercises

1. Create `x = linspace(0, 2*pi, 200)` and plot `sin(x)`, `cos(x)`,
   and `sin(x).*cos(x)` on the same axes.

2. Build a 4-by-4 matrix, select the second row, the last column, and
   the center 2-by-2 block.

3. Write a function `rmsValue(x)` that returns
   `sqrt(mean(x .* x))`.

4. Create a struct named `experiment` with fields `name`, `samples`,
   `time`, and `signal`.

5. Use `solve` to solve `x^2 - 5*x + 6 == 0`.

6. Use `0xFFs8`, `dec2hex`, and `bitand` to explore integer literal
   behavior.

7. Add breakpoints to a loop and watch the workspace update as the
   script runs.

## 34. Quick Reference

```mathtool
% Help
help plot
doc matrices
lookfor eigen

% Workspace
who
cwd
clear

% Vectors and matrices
v = [1 2 3];
A = [1 2; 3 4];
A(2, :)
A(:, end)

% Ranges
1:10
0:0.1:1

% Plotting
plot(x, y, "r--", "LineWidth", 2);
title("Title");
xlabel("x");
ylabel("y");
grid on;
hold on;
hold off;

% Functions
function y = square(x)
    y = x ^ 2;
end

% Symbolic
syms x
solve(x^2 - 1 == 0, x)

% Structs
s.name = "Alice";
s.score = 95;
```

Keep this tutorial open while experimenting. Most features are easiest
to learn by typing a small example, inspecting the Workspace panel, and
then asking `help` or `doc` for the next function you need.
