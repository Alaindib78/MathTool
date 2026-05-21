function y = centered_moving_average(x, window)
% CENTERED_MOVING_AVERAGE Smooths data with a centered moving average.
% Inputs: x is a sample vector, window is the approximate window width.
% Returns: y has the same length as x.
% Algorithm: average a clipped symmetric neighborhood around each sample.
    n = length(x);

    if window < 1
        error("centered_moving_average: window must be positive");
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

        total = 0;
        count = 0;

        for j = first:last
            total = total + x(j);
            count = count + 1;
        end

        value = total / count;
        y = [y, value];
    end
end
