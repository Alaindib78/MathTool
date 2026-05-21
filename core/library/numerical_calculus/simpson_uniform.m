function area = simpson_uniform(y, dx)
% SIMPSON_UNIFORM Integrates uniformly spaced data with Simpson's rule.
% Inputs: y is a vector with an odd number of samples, dx is spacing.
% Returns: area is the Simpson one-third integral estimate.
% Algorithm: use endpoint, 4x odd interval, and 2x even interval weights.
    n = length(y);

    if n < 3 || mod(n, 2) == 0
        error("simpson_uniform: sample count must be odd and at least three");
    end

    total = y(1) + y(n);

    for i = 2:n - 1
        if mod(i, 2) == 0
            total = total + 4 * y(i);
        else
            total = total + 2 * y(i);
        end
    end

    area = dx * total / 3;
end
