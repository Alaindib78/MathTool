function d = poly_derivative_coeffs(c)
% POLY_DERIVATIVE_COEFFS Differentiates polynomial coefficients.
% Inputs: c contains descending-power polynomial coefficients.
% Returns: d contains descending-power coefficients of the derivative.
% Algorithm: multiply each coefficient by its power and drop the constant.
    n = length(c);

    if n == 1
        d = [0];
        return;
    end

    d = [];

    for i = 1:n - 1
        power = n - i;
        value = c(i) * power;
        d = [d, value];
    end
end
