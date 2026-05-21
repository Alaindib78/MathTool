function se = standard_error_mean(x)
% STANDARD_ERROR_MEAN Estimates the standard error of the sample mean.
% Inputs: x is a sample vector.
% Returns: se is sample_std(x)/sqrt(n).
% Algorithm: divide unbiased sample standard deviation by sqrt(sample count).
    se = sample_std(x) / sqrt(length(x));
end
