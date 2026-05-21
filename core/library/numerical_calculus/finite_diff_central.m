function dy = finite_diff_central(y, dx)
% FINITE_DIFF_CENTRAL Computes a first derivative estimate for each sample.
% Inputs: y is a vector of samples, dx is uniform sample spacing.
% Returns: dy has the same length as y.
% Algorithm: use one-sided endpoints and central differences inside.
    n = length(y);

    if n < 2
        error("finite_diff_central: at least two samples are required");
    end

    dy = [];
    value = (y(2) - y(1)) / dx;
    dy = [dy, value];

    for i = 2:n - 1
        value = (y(i + 1) - y(i - 1)) / (2 * dx);
        dy = [dy, value];
    end

    value = (y(n) - y(n - 1)) / dx;
    dy = [dy, value];
end
