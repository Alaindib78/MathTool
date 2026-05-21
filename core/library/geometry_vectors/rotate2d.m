function q = rotate2d(p, theta)
% ROTATE2D Rotates a 2D point or vector about the origin.
% Inputs: p is a length-2 vector, theta is angle in radians.
% Returns: q is the rotated length-2 vector.
% Algorithm: multiply by the standard 2D rotation matrix.
    c = cos(theta);
    s = sin(theta);
    x = c * p(1) - s * p(2);
    y = s * p(1) + c * p(2);
    q = [x, y];
end
