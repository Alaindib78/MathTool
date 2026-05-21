function y = cumulative_max_values(x)
% CUMULATIVE_MAX_VALUES Computes the running maximum of a vector.
% Inputs: x is a data vector.
% Returns: y(i) is max(x(1:i)).
% Algorithm: scan once while carrying the best value so far.
    n = length(x);

    if n < 1
        error("cumulative_max_values: at least one sample is required");
    end

    best = x(1);
    y = [best];

    for i = 2:n
        if x(i) > best
            best = x(i);
        end

        y = [y, best];
    end
end
