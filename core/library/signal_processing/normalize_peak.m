function y = normalize_peak(x)
% NORMALIZE_PEAK Scales a signal so its largest absolute sample is one.
% Inputs: x is a sample vector.
% Returns: y is x divided by max(abs(x)), or x if the peak is zero.
% Algorithm: compute peak magnitude and scale all samples by it.
    peak = max(abs(x));

    if peak == 0
        y = x;
        return;
    end

    y = x ./ peak;
end
