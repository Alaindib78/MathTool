function s = sample_std(x)
% SAMPLE_STD Computes unbiased sample standard deviation.
% Inputs: x is a sample vector.
% Returns: s is sqrt(sample_variance(x)).
% Algorithm: compute sample variance and take its square root.
    s = sqrt(sample_variance(x));
end
