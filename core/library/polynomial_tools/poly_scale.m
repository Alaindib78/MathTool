function y = poly_scale(c, scale)
% POLY_SCALE Multiplies all polynomial coefficients by a scalar.
% Inputs: c is a coefficient vector, scale is a scalar.
% Returns: y is scale*c.
% Algorithm: use element-wise scalar multiplication.
    y = scale * c;
end
