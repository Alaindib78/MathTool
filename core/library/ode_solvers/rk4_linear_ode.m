function y = rk4_linear_ode(a, b, u, y0, dt)
% RK4_LINEAR_ODE Solves y' = a*y + b*u(t) with fourth-order Runge-Kutta.
% Inputs: a and b are scalar model coefficients, u is sampled input.
% Returns: y is the sampled state response starting at y0.
% Algorithm: use RK4 slopes with midpoint input approximated by averaging samples.
    n = length(u);
    y = [y0];

    for k = 2:n
        u0 = u(k - 1);
        u1 = u(k);
        umid = (u0 + u1) / 2;

        k1 = a * y(k - 1) + b * u0;
        k2 = a * (y(k - 1) + dt * k1 / 2) + b * umid;
        k3 = a * (y(k - 1) + dt * k2 / 2) + b * umid;
        k4 = a * (y(k - 1) + dt * k3) + b * u1;

        value = y(k - 1) + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6;
        y = [y, value];
    end
end
