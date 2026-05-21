function c = covariance_pair(x, y)
% COVARIANCE_PAIR Computes unbiased covariance for paired samples.
% Inputs: x and y are equal-length sample vectors.
% Returns: c is sum((x-mean(x))*(y-mean(y)))/(n-1).
% Algorithm: loop through paired residual products.
    n = length(x);

    if n < 2 || length(y) ~= n
        error("covariance_pair: vectors must have the same length >= 2");
    end

    mx = mean(x);
    my = mean(y);
    total = 0;

    for i = 1:n
        total = total + (x(i) - mx) * (y(i) - my);
    end

    c = total / (n - 1);
end
