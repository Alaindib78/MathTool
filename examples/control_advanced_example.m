% Extended control-system analysis examples for MathTool.

s = tf("s");

G = 10 / (s * (s + 1) * (s + 5));

print(G);

m = margin(G);
print(m);

rlocus(G);
bode(G);

plant = 1 / (s^2 + 2*s + 1);
controller = pid(1, 0.5, 0.1);
closed_loop = feedback(controller * plant, 1);

step(closed_loop);
print(pole(closed_loop));
print(stepinfo(closed_loop));

A = [0 1;
    -2 -3];
B = [0;
     1];
C = [1 0];
D = [0];

sys = ss(A, B, C, D);

Co = ctrb(sys);
Ob = obsv(sys);

print(rank(Co));
print(rank(Ob));

Q = [1 0;
     0 1];
R = [1];

result = lqr(A, B, Q, R);
print(result);

sysd = c2d(sys, 0.1);
print(sysd);
print(isdt(sysd));
