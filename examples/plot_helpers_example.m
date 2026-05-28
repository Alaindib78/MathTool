% MATLAB-style plotting helper commands.

x = 0:0.1:10;
y1 = sin(x);
y2 = cos(x);

figure(1);
plot(x, y1, x, y2);
title("Ticks, labels, reference lines, and legend");
xlabel("x");
ylabel("value");
xticks([0 2 4 6 8 10]);
xticklabels("zero", "two", "four", "six", "eight", "ten");
yticks([-1 0 1]);
yticklabels("low", "zero", "high");
xline(3, "--r", "x = 3");
yline(0, ":k", "zero");
legend("sin(x)", "cos(x)", "Location", "northeast");
axis([0 10 -1.5 1.5]);

figure(2);
subplot(2,1,1);
plot(x, y1);
title("Sine");
yline(0);
axis tight;

subplot(2,1,2);
plot(x, y2);
title("Cosine");
xline(5);
axis equal;
