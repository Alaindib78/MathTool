function metrics = second_order_step_metrics(zeta, wn)
% SECOND_ORDER_STEP_METRICS Estimates common second-order step metrics.
% Inputs: zeta is damping ratio, wn is natural frequency in rad/s.
% Returns: metrics is [percentOvershoot, settlingTime, peakTime, riseTime].
% Algorithm: use standard underdamped approximations and 2 percent settling.
    if zeta <= 0 || wn <= 0
        error("second_order_step_metrics: zeta and wn must be positive");
    end

    settlingTime = 4 / (zeta * wn);
    riseTime = 1.8 / wn;

    if zeta < 1
        percentOvershoot = 100 * exp(-zeta * pi / sqrt(1 - zeta ^ 2));
        peakTime = pi / (wn * sqrt(1 - zeta ^ 2));
    else
        percentOvershoot = 0;
        peakTime = 0;
    end

    metrics = [percentOvershoot, settlingTime, peakTime, riseTime];
end
