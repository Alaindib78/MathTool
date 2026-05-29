# Linear LTI Models

MathTool supports a compact MATLAB-style subset of Control System Toolbox LTI workflows.

## Constructors

```matlab
sys = ss(A, B, C, D)
sys = ss(A, B, C, D, Ts)

sys = tf(num, den)
sys = tf(num, den, Ts)

sys = zpk(z, p, k)
sys = zpk(z, p, k, Ts)

sys = frd(response, frequencies)
```

`Ts = 0` or omitted creates a continuous-time model. `Ts > 0` creates a discrete-time model.

## Conversion

The constructor names also convert between representations:

```matlab
sys_tf = tf(sys)
sys_ss = ss(sys)
sys_zpk = zpk(sys)
```

Conversions use `scipy.signal`:

- `ss2tf` for state-space to transfer function
- `tf2ss` for transfer function to state space
- `tf2zpk` and `zpk2tf` for zero-pole-gain conversion

## Inspection

```matlab
print(sys)
props = get(sys)
A = sys.A
Ts = sys.Ts
```

LTI models appear in the workspace as `tf model`, `ss model`, or `zpk model`. The variable editor shows model properties read-only.

## Analysis And Plots

```matlab
p = pole(sys)
z = zero(sys)
isstable(sys)
dcgain(sys)
damp(sys)
minreal(sys)
step(sys)
impulse(sys)
initial(sys, x0)
lsim(sys, u, t)
stepinfo(sys)
bode(sys)
bodemag(sys)
nyquist(sys)
nichols(sys)
sigma(sys)
freqresp(sys, w)
bandwidth(sys)
```

Plots are created through MathTool's existing embedded plotting system.

## Transfer Variable

```matlab
s = tf('s');
G = 1.5 / (s^2 + 14*s + 40.02);
```

Use `z = tf('z', Ts)` for discrete-time transfer-variable models.

## Stability Margins And Root Locus

```matlab
s = tf('s');
G = 10 / (s * (s + 1) * (s + 5));

m = margin(G);
all = allmargin(G);
rlocus(G);
```

`margin` uses a dense Bode grid to estimate gain margin, phase margin,
and crossover frequencies. `rlocus` computes closed-loop poles of
unity-feedback systems across a gain vector.

## Interconnections And Controllers

```matlab
G1 = tf([1], [1 1]);
G2 = tf([1], [1 2]);

series_sys = series(G1, G2);
parallel_sys = parallel(G1, G2);
closed_loop = feedback(G1, 1);

C = pid(1, 0.5, 0.1);
T = feedback(C * G1, 1);
```

Basic state-feedback synthesis is available:

```matlab
A = [0 1; -2 -3];
B = [0; 1];
Q = [1 0; 0 1];
R = [1];

result = lqr(A, B, Q, R);
K = result.K;
```

## State-Space Tools

```matlab
Co = ctrb(A, B);
Ob = obsv(A, C);
Wc = gram(sys, 'c');

X = lyap(A, Q);
S = care(A, B, Q, R);
K = place(A, B, [-2 -3]);
```

## Discrete-Time Conversion

```matlab
sysd = c2d(sys, 0.01);
sysd_tustin = c2d(sys, 0.01, 'tustin');
isdt(sysd);
isct(sys);
```

## Current Limitations

- Transfer-function arithmetic and interconnections are SISO only.
- State-space models can store MIMO matrices, but conversion and response plotting currently require SISO systems.
- Delays are stored and displayed, but response analysis ignores them with a warning.
- FRD models are SISO and interpolation-based.
- `margin`, `bandwidth`, `stepinfo`, and `pidtune` are educational approximations.
- `d2c`, MIMO transfer-function matrices, model reduction, and advanced robust-control tools are not implemented.
- LTI property dot assignment is limited to known model properties.
