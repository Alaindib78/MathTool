function r = correlation_coeff(x, y)
% CORRELATION_COEFF Computes the Pearson correlation coefficient.
% Inputs: x and y are equal-length sample vectors.
% Returns: r is covariance_pair(x,y)/(sample_std(x)*sample_std(y)).
% Algorithm: normalize covariance by the product of sample standard deviations.
    sx = sample_std(x);
    sy = sample_std(y);

    if sx == 0 || sy == 0
        error("correlation_coeff: standard deviation must be nonzero");
    end

    r = covariance_pair(x, y) / (sx * sy);
end
