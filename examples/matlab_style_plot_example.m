% =========================================================
% MathTool MATLAB-Style Plot Example
% =========================================================
% Demonstrates expanded plot syntax:
%
% - plot(Y)
% - plot(X, Y)
% - plot(X1, Y1, X2, Y2)
% - plot(X, Y, LineSpec)
% - plot(___, Name, Value)
% - hold on / hold off
% - grid on / grid off
% =========================================================

% ---------------------------------------------------------
% Simple line plot
% ---------------------------------------------------------

x = 0:pi/100:2*pi;
y = sin(x);

figure(1);
plot(x, y);
title("Simple Sine Plot");
xlabel("x");
ylabel("sin(x)");
grid on;


% ---------------------------------------------------------
% Multiple X/Y pairs in one plot call
% ---------------------------------------------------------

y1 = sin(x);
y2 = cos(x);
y3 = sin(x) .* cos(x);

figure(2);
plot(x, y1, "g", x, y2, "b--o", x, y3, "c*");
title("Multiple Lines with LineSpec");
xlabel("x");
ylabel("value");
grid on;


% ---------------------------------------------------------
% Matrix columns
% ---------------------------------------------------------

Y = [
    1 3 5;
    2 4 6;
    3 5 7;
    4 6 8
];

figure(3);
plot(Y);
title("Each Matrix Column Becomes a Line");
xlabel("row index");
ylabel("column value");
grid on;


% ---------------------------------------------------------
% Name-value properties
% ---------------------------------------------------------

figure(4);
plot(
    x,
    y1,
    "--gs",
    "LineWidth",
    2,
    "MarkerSize",
    6,
    "MarkerEdgeColor",
    "b",
    "MarkerFaceColor",
    [0.5 0.5 0.5]
);
title("LineSpec with Name-Value Properties");
xlabel("x");
ylabel("sin(x)");
grid on;


% ---------------------------------------------------------
% RGB color and a single point
% ---------------------------------------------------------

figure(5);
plot(x, cos(5 .* x), "Color", [0 0.7 0.9], "LineWidth", 2);
hold on;
plot(1, 0, "ro", "MarkerSize", 10);
hold off;
title("RGB Color and Single Point");
xlabel("x");
ylabel("cos(5x)");
grid on;

disp("MATLAB-style plot example complete");
