% =========================================================
% SECTION 14 — Recursive-like Stress
% =========================================================

TEMP = 0;

for i = 1:100
    TEMP = TEMP + sin(i);
end

print("Stress loop complete");

% =========================================================
% SECTION 15 — Strings
% =========================================================

STR1 = "Hello";
STR2 = "MathTool";
STR3 = "Debugger Test";

print(STR1);
print(STR2);
print(STR3);

print("String handling complete");

% =========================================================
% SECTION 16 — Plotting
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

print("Plotting complete");

% =========================================================
% SECTION 18 — Workspace Test Variables
% =========================================================

workspace_scalar = 123;

workspace_vector = [1 2 3 4 5];

workspace_matrix = [1 2;
                    3 4];

workspace_string = "Workspace Test";

print("Workspace variables created");

% =========================================================
% SECTION 20 — Long Running Thread Test
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

print("Long execution test complete");


