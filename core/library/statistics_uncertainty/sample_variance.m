function v = sample_variance(x)
% SAMPLE_VARIANCE Computes unbiased sample variance.
% Inputs: x is a sample vector.
% Returns: v is sum((x-mean(x))^2)/(n-1).
% Algorithm: subtract the mean, square residuals, and divide by n-1.
    n = length(x);

    if n < 2
        error("sample_variance: at least two samples are required");
    end

    m = mean(x);
    d = x - m;
    v = sum(d .* d) / (n - 1);
end
