function omega = rpm_to_rad_per_sec(rpm)
% RPM_TO_RAD_PER_SEC Converts rotational speed from rpm to rad/s.
% Inputs: rpm is revolutions per minute.
% Returns: omega is radians per second.
% Algorithm: multiply by 2*pi/60.
    omega = rpm * 2 * pi / 60;
end
