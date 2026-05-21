function area = cumulative_trapz_uniform(y, dx)
% CUMULATIVE_TRAPZ_UNIFORM Computes cumulative trapezoidal area.
% Inputs: y is a vector of samples, dx is uniform sample spacing.
% Returns: area has the same length as y and starts at zero.
% Algorithm: add dx*(y(i-1)+y(i))/2 for each interval.
    n = length(y);

    if n < 1
        error("cumulative_trapz_uniform: at least one sample is required");
    end

    area = [0];
    total = 0;

    for i = 2:n
        total = total + dx * (y(i - 1) + y(i)) / 2;
        area = [area, total];
    end
end
