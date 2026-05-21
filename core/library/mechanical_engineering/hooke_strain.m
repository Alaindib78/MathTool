function strain = hooke_strain(stress, E)
% HOOKE_STRAIN Computes strain from stress and Young's modulus.
% Inputs: stress is normal stress, E is Young's modulus.
% Returns: strain is stress/E.
% Algorithm: rearrange Hooke's law.
    if E == 0
        error("hooke_strain: modulus must be nonzero");
    end

    strain = stress / E;
end
