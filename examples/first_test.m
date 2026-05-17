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

print("Basic arithmetic complete");


% =========================================================
% SECTION 2 — Unary Operators
% =========================================================

N1 = -5;
N2 = +10;

print("Unary operators complete");


% =========================================================
% SECTION 3 — Logical Expressions
% =========================================================

L1 = A > B;
L2 = A < B;
L3 = A == 5;
L4 = A != B;
L5 = (A > 1) && (B < 10);
L6 = (A < 1) || (B < 10);

print("Logical expressions complete");


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

print("Matrix creation complete");


% =========================================================
% SECTION 5 — Transpose
% =========================================================

T1 = M1';
T2 = M3';

print("Transpose complete");


% =========================================================
% SECTION 6 — Range Expressions
% =========================================================

R1 = 1:10;
R2 = 0:0.5:5;
R3 = -5:1:5;

print("Range expressions complete");


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

print("Matrix arithmetic complete");


% =========================================================
% SECTION 8 — Element-wise Operations
% =========================================================

EV1 = [1 2 3];
EV2 = [4 5 6];

EV3 = EV1 .* EV2;
EV4 = EV2 ./ EV1;
EV5 = EV1 .^ 2;

print("Element-wise operations complete");


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

print("If statement complete");


% =========================================================
% SECTION 10 — While Loop
% =========================================================

COUNT = 0;
SUM1 = 0;

while COUNT < 10
    COUNT = COUNT + 1;
    SUM1 = SUM1 + COUNT;
end

print("While loop complete");


% =========================================================
% SECTION 11 — For Loop
% =========================================================

SUM2 = 0;

for i = 1:20
    SUM2 = SUM2 + i;
end

print("For loop complete");


% =========================================================
% SECTION 12 — Nested Loops
% =========================================================

GRID = [0 0 0 0 0;0 0 0 0 0; 0 0 0 0 0; 0 0 0 0 0;0 0 0 0 0];

for r = 1:5
    for c = 1:5
        GRID(r, c) = r * c;
    end
end

print("Nested loops complete");


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

print("Functions complete");
