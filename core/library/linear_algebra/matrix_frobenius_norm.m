function y = matrix_frobenius_norm(A)
% MATRIX_FROBENIUS_NORM Computes the Frobenius norm of a matrix.
% Inputs: A is a matrix.
% Returns: y is sqrt(sum(abs(A_ij)^2)).
% Algorithm: sum all squared magnitudes and take the square root.
    y = sqrt(sum(abs(A) .* abs(A)));
end
