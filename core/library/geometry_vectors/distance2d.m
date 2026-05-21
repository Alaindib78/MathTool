function d = distance2d(p, q)
% DISTANCE2D Computes the distance between two 2D points.
% Inputs: p and q are length-2 point vectors.
% Returns: d is Euclidean distance.
% Algorithm: apply sqrt(dx^2+dy^2).
    dx = p(1) - q(1);
    dy = p(2) - q(2);
    d = sqrt(dx * dx + dy * dy);
end
