function d = point_line_distance2d(p, a, b)
% POINT_LINE_DISTANCE2D Computes distance from point p to line through a and b.
% Inputs: p, a, and b are length-2 point vectors.
% Returns: d is the perpendicular distance to the infinite line.
% Algorithm: divide the 2D cross-product magnitude by line length.
    dx = b(1) - a(1);
    dy = b(2) - a(2);
    denom = sqrt(dx * dx + dy * dy);

    if denom == 0
        error("point_line_distance2d: line endpoints must differ");
    end

    d = abs(dy * p(1) - dx * p(2) + b(1) * a(2) - b(2) * a(1)) / denom;
end
