function zeta = damping_ratio_from_overshoot(percentOvershoot)
% DAMPING_RATIO_FROM_OVERSHOOT Estimates damping ratio from percent overshoot.
% Inputs: percentOvershoot is peak overshoot in percent.
% Returns: zeta is the corresponding underdamped damping ratio.
% Algorithm: invert Mp = exp(-zeta*pi/sqrt(1-zeta^2)).
    if percentOvershoot <= 0 || percentOvershoot >= 100
        error("damping_ratio_from_overshoot: overshoot must be between 0 and 100");
    end

    mp = percentOvershoot / 100;
    lnmp = log(mp);
    zeta = -lnmp / sqrt(pi ^ 2 + lnmp ^ 2);
end
