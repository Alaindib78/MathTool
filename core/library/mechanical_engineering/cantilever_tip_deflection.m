function delta = cantilever_tip_deflection(pointLoad, length, E, I)
% CANTILEVER_TIP_DEFLECTION Computes tip deflection of a cantilever beam.
% Inputs: pointLoad is end load, length is beam length, E and I are stiffness terms.
% Returns: delta is pointLoad*length^3/(3*E*I).
% Algorithm: apply the Euler-Bernoulli small-deflection formula.
    if E == 0 || I == 0
        error("cantilever_tip_deflection: E and I must be nonzero");
    end

    delta = pointLoad * length ^ 3 / (3 * E * I);
end
