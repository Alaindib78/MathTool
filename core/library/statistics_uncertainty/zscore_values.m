function z = zscore_values(x)
% ZSCORE_VALUES Standardizes samples to zero mean and unit sample deviation.
% Inputs: x is a sample vector.
% Returns: z contains (x-mean(x))/sample_std(x).
% Algorithm: subtract the mean and divide by unbiased sample standard deviation.
    m = mean(x);
    s = sample_std(x);

    if s == 0
        error("zscore_values: standard deviation must be nonzero");
    end

    z = (x - m) ./ s;
end
