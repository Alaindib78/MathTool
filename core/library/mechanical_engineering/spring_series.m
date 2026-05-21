function k = spring_series(k1, k2)
% SPRING_SERIES Computes equivalent stiffness of two springs in series.
% Inputs: k1 and k2 are spring stiffnesses.
% Returns: k is equivalent series stiffness.
% Algorithm: use k = k1*k2/(k1+k2).
    if k1 + k2 == 0
        error("spring_series: sum of stiffnesses must be nonzero");
    end

    k = k1 * k2 / (k1 + k2);
end
