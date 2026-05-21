function Gy = grid_gradient_y(Z, dy)
% GRID_GRADIENT_Y Estimates dZ/dy across matrix rows.
% Inputs: Z is a sampled grid, dy is row spacing.
% Returns: Gy is the same size as Z.
% Algorithm: use one-sided edge differences and central interior differences.
    rows = size(Z, 1);
    cols = size(Z, 2);

    if rows < 2
        error("grid_gradient_y: at least two rows are required");
    end

    Gy = zeros(rows, cols);

    for j = 1:cols
        Gy(1, j) = (Z(2, j) - Z(1, j)) / dy;

        for i = 2:rows - 1
            Gy(i, j) = (Z(i + 1, j) - Z(i - 1, j)) / (2 * dy);
        end

        Gy(rows, j) = (Z(rows, j) - Z(rows - 1, j)) / dy;
    end
end
