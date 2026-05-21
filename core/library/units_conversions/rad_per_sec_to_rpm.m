function rpm = rad_per_sec_to_rpm(omega)
% RAD_PER_SEC_TO_RPM Converts rotational speed from rad/s to rpm.
% Inputs: omega is radians per second.
% Returns: rpm is revolutions per minute.
% Algorithm: multiply by 60/(2*pi).
    rpm = omega * 60 / (2 * pi);
end
