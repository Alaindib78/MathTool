function wn = natural_frequency_from_settling(zeta, settlingTime)
% NATURAL_FREQUENCY_FROM_SETTLING Estimates wn from 2 percent settling time.
% Inputs: zeta is damping ratio, settlingTime is seconds.
% Returns: wn is natural frequency in rad/s.
% Algorithm: rearrange settlingTime approximately equal to 4/(zeta*wn).
    if zeta <= 0 || settlingTime <= 0
        error("natural_frequency_from_settling: inputs must be positive");
    end

    wn = 4 / (zeta * settlingTime);
end
