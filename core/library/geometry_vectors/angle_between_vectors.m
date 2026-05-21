function theta = angle_between_vectors(a, b)
% ANGLE_BETWEEN_VECTORS Computes the angle between two vectors in radians.
% Inputs: a and b are nonzero vectors.
% Returns: theta is the angle in radians.
% Algorithm: use acos(dot(a,b)/(norm(a)*norm(b))) with scalar clamping.
    denom = vec_norm(a) * vec_norm(b);

    if denom == 0
        error("angle_between_vectors: vectors must be nonzero");
    end

    c = dot(a, b) / denom;

    if c > 1
        c = 1;
    elseif c < -1
        c = -1;
    end

    theta = acos(c);
end
