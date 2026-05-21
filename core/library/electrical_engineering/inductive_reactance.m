function x = inductive_reactance(l, f)
% INDUCTIVE_REACTANCE Computes inductor reactance.
% Inputs: l is inductance in henries, f is frequency in hertz.
% Returns: x is reactance in ohms.
% Algorithm: evaluate 2*pi*f*L.
    x = 2 * pi * f * l;
end
