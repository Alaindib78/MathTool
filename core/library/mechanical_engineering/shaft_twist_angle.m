function theta = shaft_twist_angle(torque, length, shearModulus, polarJ)
% SHAFT_TWIST_ANGLE Computes twist angle for a circular shaft.
% Inputs: torque, length, shearModulus, and polarJ define the shaft.
% Returns: theta is twist angle in radians.
% Algorithm: apply theta = T*L/(G*J).
    if shearModulus == 0 || polarJ == 0
        error("shaft_twist_angle: shearModulus and polarJ must be nonzero");
    end

    theta = torque * length / (shearModulus * polarJ);
end
