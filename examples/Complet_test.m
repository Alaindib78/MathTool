% =========================================================
% MathTool Comprehensive Feature Test Script
% =========================================================
% This script is intended to test:
%
% 1. Variables
% 2. Arithmetic
% 3. Matrices
% 4. Transpose
% 5. Ranges
% 6. Functions
% 7. If / ElseIf / Else
% 8. While loops
% 9. For loops
% 10. Plotting
% 11. Workspace panel
% 12. Variable editor
% 13. REPL interaction
% 14. Debugger stepping
% 15. Breakpoints
% 16. Threaded execution
% 17. Autocomplete
% 18. Comments
% 19. Strings
% 20. Matrix operations
% 21. Symbolic variables
% 22. Complex numbers and helpers
% 23. Symbolic solve
%
% Recommended:
% - Set breakpoints manually
% - Step through execution
% - Inspect workspace continuously
% =========================================================

% =========================================================
% SECTION 1 — Basic Arithmetic
% =========================================================

A = 5;
B = 3;

C = A + B;
D = A - B;
E = A * B;
F = A / B;
G = A ^ 2;

disp("Basic arithmetic complete");


% =========================================================
% SECTION 2 — Unary Operators
% =========================================================

N1 = -5;
N2 = +10;

disp("Unary operators complete");


% =========================================================
% SECTION 3 — Logical Expressions
% =========================================================

L1 = A > B;
L2 = A < B;
L3 = A == 5;
L4 = A ~= B;
L5 = (A > 1) && (B < 10);
L6 = (A < 1) || (B < 10);
L7 = ~(A < B);

disp("Logical expressions complete");


% =========================================================
% SECTION 4 — Matrix Creation
% =========================================================

M1 = [1 2 3];
M2 = [1 -1; 2 2];
M3 = [1 2 3;
      4 5 6;
      7 8 9];

M4 = zeros(3);
M5 = ones(2);

disp("Matrix creation complete");


% =========================================================
% SECTION 5 — Transpose
% =========================================================

T1 = M1';
T2 = M3';

disp("Transpose complete");


% =========================================================
% SECTION 6 — Range Expressions
% =========================================================

R1 = 1:10;
R2 = 0:0.5:5;
R3 = -5:1:5;

disp("Range expressions complete");


% =========================================================
% SECTION 7 — Matrix Arithmetic
% =========================================================

MX1 = [1 2;
       3 4];

MX2 = [5 6;
       7 8];

MX3 = MX1 + MX2;
MX4 = MX1 - MX2;
MX5 = MX1 * MX2;

disp("Matrix arithmetic complete");


% =========================================================
% SECTION 8 — Element-wise Operations
% =========================================================

EV1 = [1 2 3];
EV2 = [4 5 6];

EV3 = EV1 .* EV2;
EV4 = EV2 ./ EV1;
EV5 = EV1 .^ 2;

disp("Element-wise operations complete");


% =========================================================
% SECTION 8B - Complex Numbers
% =========================================================

IMAG_UNIT_I = i;
IMAG_UNIT_J = j;

COMPLEX_LITERAL = 1 + 2i;
COMPLEX_LITERAL_J = 3 - 4j;
COMPLEX_FROM_FUNCTION = complex(5, -6);

COMPLEX_SQRT = sqrt(-1);

COMPLEX_R = 4;
COMPLEX_THETA = pi / 4;
COMPLEX_POLAR = COMPLEX_R * exp(1i * COMPLEX_THETA);

COMPLEX_X = [1:4]';
COMPLEX_Y = [8:-2:2]';
COMPLEX_COLUMN = COMPLEX_X + 1i * COMPLEX_Y;

COMPLEX_VECTOR = [1+2i 3-4j];

COMPLEX_PHASE = angle(COMPLEX_LITERAL);
COMPLEX_PHASE_VECTOR = angle(COMPLEX_VECTOR);

COMPLEX_CONJ = conj(COMPLEX_LITERAL);
COMPLEX_CONJ_VECTOR = conj(COMPLEX_VECTOR);

COMPLEX_REAL = real(COMPLEX_LITERAL);
COMPLEX_REAL_VECTOR = real(COMPLEX_VECTOR);

COMPLEX_IMAG = imag(COMPLEX_LITERAL);
COMPLEX_IMAG_VECTOR = imag(COMPLEX_VECTOR);

COMPLEX_ISREAL_TRUE = isreal([1 2 3]);
COMPLEX_ISREAL_FALSE = isreal(COMPLEX_VECTOR);
COMPLEX_ISREAL_STORAGE = isreal(complex(1, 0));

disp("Complex numbers complete");


% =========================================================
% SECTION 9 — If / ElseIf / Else
% =========================================================

X = 15;

if X < 0
    RESULT = -1;

elseif X == 0
    RESULT = 0;

elseif X < 10
    RESULT = 1;

else
    RESULT = 2;
end

disp("If statement complete");


% =========================================================
% SECTION 10 — While Loop
% =========================================================

COUNT = 0;
SUM1 = 0;

while COUNT < 10
    COUNT = COUNT + 1;
    SUM1 = SUM1 + COUNT;
end

disp("While loop complete");


% =========================================================
% SECTION 11 — For Loop
% =========================================================

SUM2 = 0;

for i = 1:20
    SUM2 = SUM2 + i;
end

disp("For loop complete");


% =========================================================
% SECTION 12 — Nested Loops
% =========================================================

GRID = zeros(5);

for r = 1:5
    for c = 1:5
        GRID(r, c) = r * c;
    end
end

disp("Nested loops complete");


% =========================================================
% SECTION 13 — Functions
% =========================================================

function y = square(x)
    y = x ^ 2;
end

function z = add(a, b)
    z = a + b;
end

function avg = average(a, b)
    avg = (a + b) / 2;
end

SQ1 = square(5);
SQ2 = square(12);

ADD1 = add(10, 20);

AVG1 = average(5, 15);

disp("Functions complete");


% =========================================================
% SECTION 14 — Recursive-like Stress
% =========================================================

TEMP = 0;

for i = 1:100
    TEMP = TEMP + sin(i);
end

disp("Stress loop complete");


% =========================================================
% SECTION 15 — Strings
% =========================================================

STR1 = "Hello";
STR2 = "MathTool";
STR3 = "Debugger Test";

disp(STR1);
disp(STR2);
disp(STR3);

disp("String handling complete");


% =========================================================
% SECTION 16 - Symbolic Variables
% =========================================================

syms sx

SX_AS_SYMBOL = sx;

sx = 1 / 33;
SX_NUMERIC_CLASS = class(sx);

sx = sym('1/33');
SX_EXACT = sx;
SX_SYMBOLIC_CLASS = class(sx);

class(sx);
ANS_AFTER_SYMBOLIC_CLASS = ans;

disp("Symbolic variables complete");


% =========================================================
% SECTION 16B - Symbolic Solve
% =========================================================

syms a b c x

SOLVE_EQN = a*x^2 + b*x + c == 0;
SOLVE_ROOTS = solve(SOLVE_EQN);
SOLVE_FOR_A = solve(SOLVE_EQN, a);
SOLVE_REAL_ONLY = solve(x^2 + 1 == 0, x, Real=true);

syms u v

SOLVE_EQNS = [2*u + v == 0, u - v == 1];
SOLVE_SYSTEM = solve(SOLVE_EQNS, [u v]);
SOLVE_VARIABLES = symvar(SOLVE_EQNS);

disp("Symbolic solve complete");


% =========================================================
% SECTION 17 — Plotting
% =========================================================

x = 0:0.01:2*pi;

y1 = sin(x);
y2 = cos(x);

plot(x, y1);

title("Sine Wave");
xlabel("x");
ylabel("sin(x)");
grid(true);

plot(x, y2);

title("Cosine Wave");
xlabel("x");
ylabel("cos(x)");
grid(true);

disp("Plotting complete");


% =========================================================
% SECTION 18 — Large Matrix Stress Test
% =========================================================

BIG = zeros(50);

for r = 1:50
    for c = 1:50
        BIG(r, c) = r + c;
    end
end

disp("Large matrix test complete");


% =========================================================
% SECTION 19 — Workspace Test Variables
% =========================================================

workspace_scalar = 123;

workspace_vector = [1 2 3 4 5];

workspace_matrix = [1 2;
                    3 4];

workspace_string = "Workspace Test";

disp("Workspace variables created");


% =========================================================
% SECTION 20 — Debugger Test Section
% =========================================================
% Recommended breakpoint locations:
%
% - COUNT = COUNT + 1
% - GRID(r, c) = r * c
% - y = x ^ 2
% - TEMP = TEMP + sin(i)
% - plot(x, y1)
%
% Test:
% - Step Into
% - Step Over
% - Continue
% - Variable inspection
% - Workspace updates
% =========================================================

DBG_SUM = 0;

for i = 1:10
    DBG_SUM = DBG_SUM + i;
end

disp(DBG_SUM);


% =========================================================
% SECTION 21 — Long Running Thread Test
% =========================================================
% Test:
% - GUI responsiveness
% - Stop button
% - Threaded execution
% =========================================================

LONG_COUNTER = 0;

for i = 1:500000
    LONG_COUNTER = LONG_COUNTER + 1;
end

disp("Long execution test complete");


% =========================================================
% SECTION 22 — Final Summary
% =========================================================

FINAL_RESULT = SUM1 + SUM2 + DBG_SUM;

disp("================================");
disp("ALL TESTS COMPLETED");
disp(FINAL_RESULT);
disp("================================");
