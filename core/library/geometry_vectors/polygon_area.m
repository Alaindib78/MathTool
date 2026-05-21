function area = polygon_area(P)
% POLYGON_AREA Computes signed-absolute area of a 2D polygon.
% Inputs: P is an N by 2 matrix of polygon vertices in order.
% Returns: area is the nonnegative polygon area.
% Algorithm: apply the shoelace sum over consecutive vertices.
    n = size(P, 1);

    if n < 3
        error("polygon_area: at least three vertices are required");
    end

    total = 0;

    for i = 1:n
        j = i + 1;

        if j > n
            j = 1;
        end

        total = total + P(i, 1) * P(j, 2) - P(j, 1) * P(i, 2);
    end

    area = abs(total) / 2;
end
