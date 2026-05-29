% Linear Time-Invariant (LTI) model examples for MathTool.

% State-space DC motor.
R = 2.0;
L = 0.5;
Km = 0.015;
Kb = 0.015;
Kf = 0.2;
J = 0.02;

A = [-R/L -Kb/L;
      Km/J -Kf/J];

B = [1/L;
     0];

C = [0 1];
D = [0];

sys_dc = ss(A, B, C, D);
print(sys_dc);

sys_tf = tf(sys_dc);
print(sys_tf);

sys_zpk = zpk(sys_dc);
print(sys_zpk);

step(sys_dc);

% Transfer function.
sys = tf(1.5, [1 14 40.02]);
print(sys);

p = pole(sys);
z = zero(sys);

step(sys);
impulse(sys);
bode(sys);

% Zero-pole-gain.
sys_z = zpk([], [-9.996 -4.004], 1.5);
print(sys_z);

tf_sys = tf(sys_z);
print(tf_sys);

% Discrete-time transfer function.
sysd = tf(1, [1 1], 0.01);
print(sysd);
step(sysd);

% Transfer variable.
s = tf('s');
G = 1.5 / (s^2 + 14*s + 40.02);
print(G);
step(G);
