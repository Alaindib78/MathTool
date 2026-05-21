function params = linear_fit_params(x, y)
% LINEAR_FIT_PARAMS Fits y = m*x + b by least squares.
% Inputs: x and y are paired sample vectors.
% Returns: params is [m, b].
% Algorithm: apply the closed-form two-parameter least-squares equations.
    n = length(x);

    if n < 2
        error("linear_fit_params: at least two samples are required");
    end

    sx = sum(x);
    sy = sum(y);
    sxx = dot(x, x);
    sxy = dot(x, y);
    denom = n * sxx - sx * sx;

    if denom == 0
        error("linear_fit_params: x samples are singular");
    end

    m = (n * sxy - sx * sy) / denom;
    b = (sy - m * sx) / n;
    params = [m, b];
end
