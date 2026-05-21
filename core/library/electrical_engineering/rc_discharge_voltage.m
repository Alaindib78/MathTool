function v = rc_discharge_voltage(v0, r, c, t)
% RC_DISCHARGE_VOLTAGE Computes capacitor voltage during RC discharge.
% Inputs: v0 is initial voltage, r and c define tau, t is time.
% Returns: v is capacitor voltage at time t.
% Algorithm: evaluate v0*exp(-t/(R*C)).
    tau = rc_time_constant(r, c);

    if tau <= 0
        error("rc_discharge_voltage: time constant must be positive");
    end

    v = v0 * exp(-t / tau);
end
