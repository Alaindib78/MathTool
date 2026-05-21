function v = ohms_voltage(i, r)
% OHMS_VOLTAGE Computes voltage from current and resistance.
% Inputs: i is current in amperes, r is resistance in ohms.
% Returns: v is voltage in volts.
% Algorithm: apply V = I*R.
    v = i * r;
end
