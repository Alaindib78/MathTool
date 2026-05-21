function p = poly_integral_coeffs(c, constant)
% POLY_INTEGRAL_COEFFS Integrates polynomial coefficients.
% Inputs: c contains descending-power coefficients, constant is integration constant.
% Returns: p contains descending-power coefficients of the antiderivative.
% Algorithm: divide each coefficient by the increased power and append constant.
    n = length(c);
    p = [];

    for i = 1:n
        power = n - i + 1;
        value = c(i) / power;
        p = [p, value];
    end

    p = [p, constant];
end
