function y = moving_average(x, window)
% MOVING_AVERAGE Computes a causal moving average.
% Inputs: x is a sample vector, window is the number of samples to average.
% Returns: y has the same length as x.
% Algorithm: average samples from max(1,i-window+1) through i.
    n = length(x);

    if window < 1
        error("moving_average: window must be positive");
    end

    y = [];

    for i = 1:n
        first = i - window + 1;

        if first < 1
            first = 1;
        end

        total = 0;
        count = 0;

        for j = first:i
            total = total + x(j);
            count = count + 1;
        end

        value = total / count;
        y = [y, value];
    end
end
