function y = matrix_inf_norm(A)
% MATRIX_INF_NORM Computes the maximum absolute row sum of a matrix.
% Inputs: A is a matrix.
% Returns: y is max_i sum_j abs(A(i,j)).
% Algorithm: loop over rows and track the largest absolute row sum.
    rows = size(A, 1);
    cols = size(A, 2);
    y = 0;

    for i = 1:rows
        total = 0;

        for j = 1:cols
            total = total + abs(A(i, j));
        end

        if total > y
            y = total;
        end
    end
end
