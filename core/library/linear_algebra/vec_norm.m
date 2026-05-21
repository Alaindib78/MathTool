function y = vec_norm(x)
% VEC_NORM Computes the Euclidean length of a vector.
% Inputs: x is a real or complex vector.
% Returns: y is sqrt(sum(abs(x)^2)).
% Algorithm: sum squared magnitudes and take the square root.
    y = sqrt(sum(abs(x) .* abs(x)));
end
