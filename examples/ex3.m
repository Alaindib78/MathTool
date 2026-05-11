t = 0:0.1:2*pi;
y1 = sin(t);
y2 = cos(t);

plot(t, y1); title("sin wave"); xlabel("time (s)"); ylabel("V (volts)"); grid(true);

plot(t, y2); title("cos wave"); xlabel("time (s)"); ylabel("V (volts)"); grid(true);