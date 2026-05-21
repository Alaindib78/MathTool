function yq = interp_linear_vector(x, y, xq)
% INTERP_LINEAR_VECTOR Interpolates many query points with clamped endpoints.
% Inputs: x and y are sorted sample vectors, xq is a vector of query points.
% Returns: yq is a vector of interpolated values.
% Algorithm: call interp_linear_clamped for each query point.
    n = length(xq);
    yq = [];

    for i = 1:n
        yq = [yq, interp_linear_clamped(x, y, xq(i))];
    end
end
