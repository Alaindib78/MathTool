function area = triangle_area_heron(a, b, c)
% TRIANGLE_AREA_HERON Computes triangle area from side lengths.
% Inputs: a, b, and c are side lengths.
% Returns: area is the triangle area.
% Algorithm: apply Heron's formula sqrt(s*(s-a)*(s-b)*(s-c)).
    if a <= 0 || b <= 0 || c <= 0
        error("triangle_area_heron: side lengths must be positive");
    end

    s = (a + b + c) / 2;
    area = sqrt(s * (s - a) * (s - b) * (s - c));
end
