function yq = interp_linear_clamped(x, y, xq)
% INTERP_LINEAR_CLAMPED Performs scalar linear interpolation with clamped ends.
% Inputs: x and y are sorted sample vectors, xq is a query location.
% Returns: yq is linearly interpolated or clamped to the endpoint value.
% Algorithm: find the containing interval and interpolate within it.
    n = length(x);

    if n < 2
        error("interp_linear_clamped: at least two samples are required");
    end

    if xq <= x(1)
        yq = y(1);
        return;
    end

    if xq >= x(n)
        yq = y(n);
        return;
    end

    for i = 1:n - 1
        if xq >= x(i) && xq <= x(i + 1)
            t = (xq - x(i)) / (x(i + 1) - x(i));
            yq = y(i) + t * (y(i + 1) - y(i));
            return;
        end
    end

    yq = y(n);
end
