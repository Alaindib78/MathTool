function m = weighted_mean(x, w)
% WEIGHTED_MEAN Computes a weighted average.
% Inputs: x is a value vector, w is a matching weight vector.
% Returns: m is sum(x*w)/sum(w).
% Algorithm: divide the weighted sum by the total weight.
    totalWeight = sum(w);

    if totalWeight == 0
        error("weighted_mean: sum of weights must be nonzero");
    end

    m = sum(x .* w) / totalWeight;
end
