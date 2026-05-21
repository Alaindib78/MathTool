function d = distance3d(p, q)
% DISTANCE3D Computes the distance between two 3D points.
% Inputs: p and q are length-3 point vectors.
% Returns: d is Euclidean distance.
% Algorithm: apply sqrt(dx^2+dy^2+dz^2).
    dx = p(1) - q(1);
    dy = p(2) - q(2);
    dz = p(3) - q(3);
    d = sqrt(dx * dx + dy * dy + dz * dz);
end
