function strain = axial_strain(deltaLength, length0)
% AXIAL_STRAIN Computes engineering axial strain.
% Inputs: deltaLength is elongation, length0 is original length.
% Returns: strain is deltaLength/length0.
% Algorithm: divide elongation by original length.
    if length0 == 0
        error("axial_strain: original length must be nonzero");
    end

    strain = deltaLength / length0;
end
