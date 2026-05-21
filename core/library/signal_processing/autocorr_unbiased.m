function r = autocorr_unbiased(x, maxLag)
% AUTOCORR_UNBIASED Computes unbiased autocorrelation estimates.
% Inputs: x is a sample vector, maxLag is the largest lag to compute.
% Returns: r contains lags 0 through maxLag.
% Algorithm: average x(i)*x(i+lag) over the available overlapping samples.
    n = length(x);

    if maxLag >= n
        error("autocorr_unbiased: maxLag must be smaller than length(x)");
    end

    r = [];

    for lag = 0:maxLag
        total = 0;

        for i = 1:n - lag
            total = total + x(i) * x(i + lag);
        end

        value = total / (n - lag);
        r = [r, value];
    end
end
