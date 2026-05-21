function idx = first_index_ge(x, value)
% FIRST_INDEX_GE Finds the first sample index with x(i) >= value.
% Inputs: x is a data vector, value is the threshold.
% Returns: idx is the one-based index, or 0 when no sample qualifies.
% Algorithm: scan from the start and return on the first qualifying sample.
    n = length(x);
    idx = 0;

    for i = 1:n
        if x(i) >= value
            idx = i;
            return;
        end
    end
end
