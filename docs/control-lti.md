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
step(sys)
impulse(sys)
bode(sys)
```

Plots are created through MathTool's existing embedded plotting system.

## Transfer Variable

```matlab
s = tf('s');
G = 1.5 / (s^2 + 14*s + 40.02);
```

## Current Limitations

- Transfer-function arithmetic is SISO only.
- State-space models can store MIMO matrices, but conversion and response plotting currently require SISO systems.
- Delays are stored and displayed, but response analysis ignores them with a warning.
- FRD models and advanced control-design tools are not implemented.
- LTI property dot assignment is limited to known model properties.
