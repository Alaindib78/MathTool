function ci = ci95_mean(x)
% CI95_MEAN Computes a normal-approximate 95 percent confidence interval.
% Inputs: x is a sample vector.
% Returns: ci is [lower, upper] for the mean.
% Algorithm: use mean(x) +/- 1.96*standard_error_mean(x).
    m = mean(x);
    halfWidth = 1.96 * standard_error_mean(x);
    lower = m - halfWidth;
    upper = m + halfWidth;
    ci = [lower, upper];
end
