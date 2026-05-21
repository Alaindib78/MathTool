function vout = voltage_divider(vin, r1, r2)
% VOLTAGE_DIVIDER Computes output of a two-resistor divider.
% Inputs: vin is source voltage, r1 is upper resistance, r2 is lower resistance.
% Returns: vout is vin*r2/(r1+r2).
% Algorithm: apply the standard unloaded divider formula.
    if r1 + r2 == 0
        error("voltage_divider: total resistance must be nonzero");
    end

    vout = vin * r2 / (r1 + r2);
end
