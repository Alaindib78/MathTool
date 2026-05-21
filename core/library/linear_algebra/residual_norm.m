function rnorm = residual_norm(A, x, b)
% RESIDUAL_NORM Measures the residual of a linear solve.
% Inputs: A is a matrix, x is a candidate solution, b is a right hand side.
% Returns: rnorm is vec_norm(A*x - b).
% Algorithm: form the residual vector and compute its Euclidean norm.
    r = A * x - b;
    rnorm = vec_norm(r);
end
