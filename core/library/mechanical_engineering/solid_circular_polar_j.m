function j = solid_circular_polar_j(diameter)
% SOLID_CIRCULAR_POLAR_J Computes polar moment for a solid circular shaft.
% Inputs: diameter is shaft diameter.
% Returns: j is pi*d^4/32.
% Algorithm: evaluate the closed-form polar second moment of area.
    j = pi * diameter ^ 4 / 32;
end
