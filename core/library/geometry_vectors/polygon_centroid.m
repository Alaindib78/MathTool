function c = polygon_centroid(P)
% POLYGON_CENTROID Computes the centroid of a non-self-intersecting polygon.
% Inputs: P is an N by 2 matrix of ordered polygon vertices.
% Returns: c is [cx, cy].
% Algorithm: use the shoelace centroid formula.
    n = size(P, 1);

    if n < 3
        error("polygon_centroid: at least three vertices are required");
    end

    crossTotal = 0;
    cx = 0;
    cy = 0;

    for i = 1:n
        j = i + 1;

        if j > n
            j = 1;
        end

        cross = P(i, 1) * P(j, 2) - P(j, 1) * P(i, 2);
        crossTotal = crossTotal + cross;
        cx = cx + (P(i, 1) + P(j, 1)) * cross;
        cy = cy + (P(i, 2) + P(j, 2)) * cross;
    end

    area = crossTotal / 2;

    if area == 0
        error("polygon_centroid: polygon area must be nonzero");
    end

    x = cx / (6 * area);
    y = cy / (6 * area);
    c = [x, y];
end
