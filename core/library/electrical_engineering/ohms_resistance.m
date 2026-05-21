function r = ohms_resistance(v, i)
% OHMS_RESISTANCE Computes resistance from voltage and current.
% Inputs: v is voltage in volts, i is current in amperes.
% Returns: r is resistance in ohms.
% Algorithm: apply R = V/I.
    if i == 0
        error("ohms_resistance: current must be nonzero");
    end

    r = v / i;
end
