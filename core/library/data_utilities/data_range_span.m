function r = data_range_span(x)
% DATA_RANGE_SPAN Computes max-min for a data vector.
% Inputs: x is a data vector.
% Returns: r is max(x)-min(x).
% Algorithm: subtract the minimum sample from the maximum sample.
    r = max(x) - min(x);
end
