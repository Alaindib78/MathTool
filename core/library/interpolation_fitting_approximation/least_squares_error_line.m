function err = least_squares_error_line(x, y, m, b)
% LEAST_SQUARES_ERROR_LINE Computes squared error for a line fit.
% Inputs: x and y are sample vectors, m and b define y = m*x+b.
% Returns: err is sum((m*x+b-y)^2).
% Algorithm: loop through samples and accumulate squared residuals.
    n = length(x);
    err = 0;

    for i = 1:n
        r = m * x(i) + b - y(i);
        err = err + r * r;
    end
end
