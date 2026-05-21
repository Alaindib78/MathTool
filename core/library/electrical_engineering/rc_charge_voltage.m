function v = rc_charge_voltage(vs, r, c, t)
% RC_CHARGE_VOLTAGE Computes capacitor voltage during RC charging.
% Inputs: vs is supply voltage, r and c define tau, t is time.
% Returns: v is capacitor voltage at time t.
% Algorithm: evaluate vs*(1-exp(-t/(R*C))).
    tau = rc_time_constant(r, c);

    if tau <= 0
        error("rc_charge_voltage: time constant must be positive");
    end

    v = vs * (1 - exp(-t / tau));
end
