function r = parallel_resistance2(r1, r2)
% PARALLEL_RESISTANCE2 Computes equivalent resistance of two parallel resistors.
% Inputs: r1 and r2 are resistances in ohms.
% Returns: r is equivalent resistance in ohms.
% Algorithm: use r = r1*r2/(r1+r2).
    if r1 + r2 == 0
        error("parallel_resistance2: sum of resistances must be nonzero");
    end

    r = r1 * r2 / (r1 + r2);
end
