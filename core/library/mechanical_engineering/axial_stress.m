function stress = axial_stress(force, area)
% AXIAL_STRESS Computes normal stress from axial load.
% Inputs: force is axial force, area is cross-sectional area.
% Returns: stress is force/area.
% Algorithm: divide force by area after checking area.
    if area == 0
        error("axial_stress: area must be nonzero");
    end

    stress = force / area;
end
