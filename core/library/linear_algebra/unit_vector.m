function y = unit_vector(x)
% UNIT_VECTOR Normalizes a vector to unit Euclidean length.
% Inputs: x is a vector.
% Returns: y is x divided by its Euclidean norm.
% Algorithm: compute vec_norm(x), reject a zero vector, then scale x.
    n = vec_norm(x);

    if n == 0
        error("unit_vector: zero vector cannot be normalized");
    end

    y = x ./ n;
end
