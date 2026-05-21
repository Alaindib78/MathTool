function i = ohms_current(v, r)
% OHMS_CURRENT Computes current from voltage and resistance.
% Inputs: v is voltage in volts, r is resistance in ohms.
% Returns: i is current in amperes.
% Algorithm: apply I = V/R.
    if r == 0
        error("ohms_current: resistance must be nonzero");
    end

    i = v / r;
end
