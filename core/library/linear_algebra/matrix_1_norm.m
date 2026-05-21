function y = matrix_1_norm(A)
% MATRIX_1_NORM Computes the maximum absolute column sum of a matrix.
% Inputs: A is a matrix.
% Returns: y is max_j sum_i abs(A(i,j)).
% Algorithm: loop over columns and track the largest absolute column sum.
    rows = size(A, 1);
    cols = size(A, 2);
    y = 0;

    for j = 1:cols
        total = 0;

        for i = 1:rows
            total = total + abs(A(i, j));
        end

        if total > y
            y = total;
        end
    end
end
