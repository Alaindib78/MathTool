function stress = hooke_stress(E, strain)
% HOOKE_STRESS Computes stress from Young's modulus and strain.
% Inputs: E is Young's modulus, strain is engineering strain.
% Returns: stress is E*strain.
% Algorithm: apply Hooke's law for a linear elastic material.
    stress = E * strain;
end
