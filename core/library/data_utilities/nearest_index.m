function idx = nearest_index(x, value)
% NEAREST_INDEX Finds the index of the sample nearest to a value.
% Inputs: x is a data vector, value is the target.
% Returns: idx is the one-based nearest sample index.
% Algorithm: scan all samples and keep the smallest absolute error.
    n = length(x);

    if n < 1
        error("nearest_index: at least one sample is required");
    end

    idx = 1;
    best = abs(x(1) - value);

    for i = 2:n
        err = abs(x(i) - value);

        if err < best
            best = err;
            idx = i;
        end
    end
end
