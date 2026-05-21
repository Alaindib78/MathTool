function stress = thin_wall_hoop_stress(pressure, radius, thickness)
% THIN_WALL_HOOP_STRESS Computes hoop stress for a thin pressure vessel.
% Inputs: pressure is internal pressure, radius is vessel radius, thickness is wall thickness.
% Returns: stress is pressure*radius/thickness.
% Algorithm: apply the thin-wall cylinder hoop stress formula.
    if thickness == 0
        error("thin_wall_hoop_stress: thickness must be nonzero");
    end

    stress = pressure * radius / thickness;
end
