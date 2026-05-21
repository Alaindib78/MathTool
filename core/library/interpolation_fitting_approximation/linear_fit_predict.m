function yq = linear_fit_predict(x, y, xq)
% LINEAR_FIT_PREDICT Predicts values from a fitted straight line.
% Inputs: x and y are sample vectors, xq is a scalar or vector of queries.
% Returns: yq equals m*xq+b using least-squares fitted m and b.
% Algorithm: compute linear_fit_params and evaluate the resulting line.
    params = linear_fit_params(x, y);
    yq = params(1) * xq + params(2);
end
