function y = clamp_value(x, lower, upper)
% CLAMP_VALUE Restricts a scalar to a closed interval.
% Inputs: x is a scalar, lower and upper are bounds.
% Returns: y is lower <= y <= upper.
% Algorithm: compare x to each bound and return the clipped value.
    if lower > upper
        error("clamp_value: lower bound must not exceed upper bound");
    end

    if x < lower
        y = lower;
    elseif x > upper
        y = upper;
    else
        y = x;
    end
end
