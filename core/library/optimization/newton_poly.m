function result = newton_poly(coeffs, x0, tol, maxIter)
% NEWTON_POLY Finds a polynomial root with Newton's method.
% Inputs: coeffs are polynomial coefficients, x0 is the initial guess.
% Returns: result is [root, f(root), iterations].
% Algorithm: compute derivative coefficients and iterate x-f(x)/f'(x).
    dcoeffs = poly_derivative_coeffs(coeffs);
    x = x0;
    iter = 0;
    step = tol + 1;

    while iter < maxIter && abs(step) > tol
        fx = polyval(coeffs, x);
        dfx = polyval(dcoeffs, x);

        if dfx == 0
            error("newton_poly: derivative became zero");
        end

        step = fx / dfx;
        x = x - step;
        iter = iter + 1;
    end

    result = [x, polyval(coeffs, x), iter];
end
