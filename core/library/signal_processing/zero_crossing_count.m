function count = zero_crossing_count(x)
% ZERO_CROSSING_COUNT Counts sign changes in a sampled signal.
% Inputs: x is a real-valued sample vector.
% Returns: count is the number of positive-to-negative or negative-to-positive crossings.
% Algorithm: scan adjacent nonzero samples and count sign changes.
    n = length(x);
    count = 0;

    if n < 2
        return;
    end

    previous = x(1);

    for i = 2:n
        current = x(i);

        if (previous < 0 && current >= 0) || (previous > 0 && current <= 0)
            count = count + 1;
        end

        if current ~= 0
            previous = current;
        end
    end
end
