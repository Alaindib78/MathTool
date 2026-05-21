function gain = dc_gain_numden(num, den)
% DC_GAIN_NUMDEN Computes DC gain from transfer-function coefficients.
% Inputs: num and den are descending-power numerator and denominator coefficients.
% Returns: gain is num(s=0)/den(s=0).
% Algorithm: divide the final numerator coefficient by the final denominator coefficient.
    nnum = length(num);
    nden = length(den);

    if den(nden) == 0
        error("dc_gain_numden: denominator constant term must be nonzero");
    end

    gain = num(nnum) / den(nden);
end
