function Gx = grid_gradient_x(Z, dx)
% GRID_GRADIENT_X Estimates dZ/dx across matrix columns.
% Inputs: Z is a sampled grid, dx is column spacing.
% Returns: Gx is the same size as Z.
% Algorithm: use one-sided edge differences and central interior differences.
    rows = size(Z, 1);
    cols = size(Z, 2);

    if cols < 2
        error("grid_gradient_x: at least two columns are required");
    end

    Gx = zeros(rows, cols);

    for i = 1:rows
        Gx(i, 1) = (Z(i, 2) - Z(i, 1)) / dx;

        for j = 2:cols - 1
            Gx(i, j) = (Z(i, j + 1) - Z(i, j - 1)) / (2 * dx);
        end

        Gx(i, cols) = (Z(i, cols) - Z(i, cols - 1)) / dx;
    end
end
