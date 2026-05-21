function y = minmax_scale(x, newMin, newMax)
% MINMAX_SCALE Rescales data into a requested numeric range.
% Inputs: x is a vector, newMin and newMax are output bounds.
% Returns: y is linearly rescaled data.
% Algorithm: map min(x) to newMin and max(x) to newMax.
    xmin = min(x);
    xmax = max(x);
    span = xmax - xmin;

    if span == 0
        error("minmax_scale: input range must be nonzero");
    end

    y = (x - xmin) ./ span;
    y = y * (newMax - newMin) + newMin;
end
