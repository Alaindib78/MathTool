% =========================================================
% MathTool Figure And Close Example
% =========================================================
% Demonstrates:
% - figure
% - figure(n)
% - close
% - close(n)
% - close all
% =========================================================

t = 0:0.05:2*pi;

% Create the next available figure.
figure
plot(t, sin(t));
title("Figure 1 - sine");
xlabel("t");
ylabel("sin(t)");
grid(true);

% Create or activate figure 2.
figure(2);
plot(t, cos(t));
title("Figure 2 - cosine");
xlabel("t");
ylabel("cos(t)");
grid(true);

% Return to figure 1 and replace/update its current plot.
figure(1);
plot(t, sin(t) .* cos(t));
title("Figure 1 - sin(t) * cos(t)");
xlabel("t");
ylabel("product");
grid(true);

% Close a specific numbered figure.
close(2);

% Create figure 3, then close the current figure.
figure(3);
plot(t, exp(t .* -0.25) .* sin(t .* 4));
title("Figure 3 - damped oscillation");
xlabel("t");
ylabel("amplitude");
grid(true);

close;

% Leave one final figure visible after the example finishes.
figure(4);
plot(t, sin(t));
title("Figure 4 - final visible figure");
xlabel("t");
ylabel("sin(t)");
grid(true);

% Close every open figure.
% This is commented so running the example leaves Figure 4 visible.
% close all

disp("Figure and close example complete");
