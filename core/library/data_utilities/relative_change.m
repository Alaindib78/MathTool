function r = relative_change(oldValue, newValue)
% RELATIVE_CHANGE Computes fractional change from old to new value.
% Inputs: oldValue is baseline, newValue is updated value.
% Returns: r is (newValue-oldValue)/oldValue.
% Algorithm: subtract baseline and divide by baseline.
    if oldValue == 0
        error("relative_change: oldValue must be nonzero");
    end

    r = (newValue - oldValue) / oldValue;
end
