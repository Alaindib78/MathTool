function dy = finite_diff_forward(y, dx)
% FINITE_DIFF_FORWARD Computes first derivatives from sampled data.
% Inputs: y is a vector of samples, dx is uniform sample spacing.
% Returns: dy contains forward differences and has length length(y)-1.
% Algorithm: use (y(i+1)-y(i))/dx for each adjacent pair.
    n = length(y);

    if n < 2
        error("finite_diff_forward: at least two samples are required");
    end

    dy = [];

    for i = 1:n - 1
        value = (y(i + 1) - y(i)) / dx;
        dy = [dy, value];
    end
end
