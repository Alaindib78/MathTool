function y = normalize_sum(x)
% NORMALIZE_SUM Scales a vector so its samples sum to one.
% Inputs: x is a data vector.
% Returns: y is x/sum(x).
% Algorithm: divide all samples by their total sum.
    total = sum(x);

    if total == 0
        error("normalize_sum: sum must be nonzero");
    end

    y = x ./ total;
end
