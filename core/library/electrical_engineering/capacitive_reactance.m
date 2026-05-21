function x = capacitive_reactance(c, f)
% CAPACITIVE_REACTANCE Computes magnitude of capacitor reactance.
% Inputs: c is capacitance in farads, f is frequency in hertz.
% Returns: x is reactance magnitude in ohms.
% Algorithm: evaluate 1/(2*pi*f*C).
    if c <= 0 || f <= 0
        error("capacitive_reactance: capacitance and frequency must be positive");
    end

    x = 1 / (2 * pi * f * c);
end
