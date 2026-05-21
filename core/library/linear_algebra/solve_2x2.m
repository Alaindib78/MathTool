function x = solve_2x2(A, b)
% SOLVE_2X2 Solves a two-equation linear system A*x = b.
% Inputs: A is a 2 by 2 matrix, b is a length-2 right hand side.
% Returns: x is the length-2 solution vector.
% Algorithm: apply the closed-form inverse using the determinant.
    detA = A(1, 1) * A(2, 2) - A(1, 2) * A(2, 1);

    if detA == 0
        error("solve_2x2: singular matrix");
    end

    x1 = (b(1) * A(2, 2) - A(1, 2) * b(2)) / detA;
    x2 = (A(1, 1) * b(2) - b(1) * A(2, 1)) / detA;
    x = [x1, x2];
end
