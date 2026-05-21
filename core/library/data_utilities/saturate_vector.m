function y = saturate_vector(x, lower, upper)
% SATURATE_VECTOR Clips every vector sample to an interval.
% Inputs: x is a vector, lower and upper are scalar limits.
% Returns: y contains clipped samples.
% Algorithm: apply clamp_value to each sample.
    n = length(x);
    y = [];

    for i = 1:n
        y = [y, clamp_value(x(i), lower, upper)];
    end
end
