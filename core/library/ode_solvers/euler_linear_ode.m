function y = euler_linear_ode(a, b, u, y0, dt)
% EULER_LINEAR_ODE Solves y' = a*y + b*u(t) with explicit Euler.
% Inputs: a and b are scalar model coefficients, u is sampled input.
% Returns: y is the sampled state response starting at y0.
% Algorithm: step y(k)=y(k-1)+dt*(a*y(k-1)+b*u(k-1)).
    n = length(u);
    y = [y0];

    for k = 2:n
        dydt = a * y(k - 1) + b * u(k - 1);
        value = y(k - 1) + dt * dydt;
        y = [y, value];
    end
end
