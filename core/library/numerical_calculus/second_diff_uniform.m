function d2y = second_diff_uniform(y, dx)
% SECOND_DIFF_UNIFORM Computes second derivatives on a uniform grid.
% Inputs: y is a vector of samples, dx is uniform sample spacing.
% Returns: d2y has length length(y)-2.
% Algorithm: use (y(i+2)-2*y(i+1)+y(i))/(dx^2).
    n = length(y);

    if n < 3
        error("second_diff_uniform: at least three samples are required");
    end

    d2y = [];

    for i = 1:n - 2
        value = (y(i + 2) - 2 * y(i + 1) + y(i)) / (dx ^ 2);
        d2y = [d2y, value];
    end
end
