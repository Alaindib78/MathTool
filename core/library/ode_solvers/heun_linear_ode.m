function y = heun_linear_ode(a, b, u, y0, dt)
% HEUN_LINEAR_ODE Solves y' = a*y + b*u(t) with Heun's method.
% Inputs: a and b are scalar model coefficients, u is sampled input.
% Returns: y is the sampled state response starting at y0.
% Algorithm: average Euler predictor and endpoint slopes.
    n = length(u);
    y = [y0];

    for k = 2:n
        f0 = a * y(k - 1) + b * u(k - 1);
        predictor = y(k - 1) + dt * f0;
        f1 = a * predictor + b * u(k);
        value = y(k - 1) + dt * (f0 + f1) / 2;
        y = [y, value];
    end
end
