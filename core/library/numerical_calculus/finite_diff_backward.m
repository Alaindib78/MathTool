function dy = finite_diff_backward(y, dx)
% FINITE_DIFF_BACKWARD Computes backward first differences.
% Inputs: y is a vector of samples, dx is uniform sample spacing.
% Returns: dy contains backward differences and has length length(y)-1.
% Algorithm: use (y(i)-y(i-1))/dx for samples after the first.
    n = length(y);

    if n < 2
        error("finite_diff_backward: at least two samples are required");
    end

    dy = [];

    for i = 2:n
        value = (y(i) - y(i - 1)) / dx;
        dy = [dy, value];
    end
end
