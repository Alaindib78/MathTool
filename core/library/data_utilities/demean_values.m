function y = demean_values(x)
% DEMEAN_VALUES Removes the arithmetic mean from data.
% Inputs: x is a data vector.
% Returns: y is x-mean(x).
% Algorithm: subtract the built-in mean from each sample.
    y = x - mean(x);
end
