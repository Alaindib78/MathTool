function tau = torsion_shear_stress_circular(torque, radius, polarJ)
% TORSION_SHEAR_STRESS_CIRCULAR Computes torsional shear stress.
% Inputs: torque is applied torque, radius is evaluation radius, polarJ is polar moment.
% Returns: tau is torque*radius/polarJ.
% Algorithm: apply the circular-shaft torsion formula.
    if polarJ == 0
        error("torsion_shear_stress_circular: polarJ must be nonzero");
    end

    tau = torque * radius / polarJ;
end
