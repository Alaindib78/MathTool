function y = peak_to_peak(x)
% PEAK_TO_PEAK Computes the full excursion of a signal.
% Inputs: x is a sample vector.
% Returns: y is max(x)-min(x).
% Algorithm: subtract the minimum sample from the maximum sample.
    y = max(x) - min(x);
end
