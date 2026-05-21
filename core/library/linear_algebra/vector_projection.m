function p = vector_projection(a, b)
% VECTOR_PROJECTION Projects vector a onto vector b.
% Inputs: a is the vector to project, b is the target direction.
% Returns: p is the component of a parallel to b.
% Algorithm: use p = (dot(a,b) / dot(b,b)) * b.
    denom = dot(b, b);

    if denom == 0
        error("vector_projection: target vector must be nonzero");
    end

    scale = dot(a, b) / denom;
    p = scale * b;
end
