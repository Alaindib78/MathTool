function y = poly_trim_leading(c, tol)
% POLY_TRIM_LEADING Removes small leading polynomial coefficients.
% Inputs: c is a coefficient vector, tol is the absolute cutoff.
% Returns: y starts at the first coefficient whose magnitude exceeds tol.
% Algorithm: advance over leading small values while keeping one coefficient.
    n = length(c);
    first = 1;

    while first < n && abs(c(first)) <= tol
        first = first + 1;
    end

    y = [];

    for i = first:n
        y = [y, c(i)];
    end
end
