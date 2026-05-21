function y = lerp_value(a, b, t)
% LERP_VALUE Computes a linear interpolation between two scalar values.
% Inputs: a and b are endpoint values, t is the interpolation fraction.
% Returns: y equals a at t=0 and b at t=1.
% Algorithm: evaluate a + t*(b-a).
    y = a + t * (b - a);
end
