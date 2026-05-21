function delta = simply_supported_center_deflection(pointLoad, length, E, I)
% SIMPLY_SUPPORTED_CENTER_DEFLECTION Computes midspan deflection for center load.
% Inputs: pointLoad is central load, length is span, E and I are stiffness terms.
% Returns: delta is pointLoad*length^3/(48*E*I).
% Algorithm: apply the standard simply supported beam formula.
    if E == 0 || I == 0
        error("simply_supported_center_deflection: E and I must be nonzero");
    end

    delta = pointLoad * length ^ 3 / (48 * E * I);
end
