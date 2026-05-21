function result = is_symmetric_matrix(A, tol)
% IS_SYMMETRIC_MATRIX Tests whether a square matrix is symmetric.
% Inputs: A is a matrix, tol is the allowed absolute difference.
% Returns: result is true when abs(A(i,j)-A(j,i)) <= tol for all entries.
% Algorithm: compare mirrored entries with nested loops.
    rows = size(A, 1);
    cols = size(A, 2);

    if rows ~= cols
        result = false;
        return;
    end

    result = true;

    for i = 1:rows
        for j = 1:cols
            if abs(A(i, j) - A(j, i)) > tol
                result = false;
                return;
            end
        end
    end
end
