function y = median_filter1d(x, window)
% MEDIAN_FILTER1D Applies a sliding median filter to one-dimensional data.
% Inputs: x is a sample vector, window is the neighborhood width.
% Returns: y has the same length as x.
% Algorithm: collect a clipped neighborhood, sort it, and take its median.
    n = length(x);

    if window < 1
        error("median_filter1d: window must be positive");
    end

    half = floor(window / 2);
    y = [];

    for i = 1:n
        first = i - half;
        last = i + half;

        if first < 1
            first = 1;
        end

        if last > n
            last = n;
        end

        values = [];

        for j = first:last
            values = [values, x(j)];
        end

        sorted = sort(values);
        m = length(sorted);

        if mod(m, 2) == 1
            mid = (m + 1) / 2;
            y = [y, sorted(mid)];
        else
            mid = m / 2;
            value = (sorted(mid) + sorted(mid + 1)) / 2;
            y = [y, value];
        end
    end
end
