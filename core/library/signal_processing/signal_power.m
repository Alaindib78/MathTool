function p = signal_power(x)
% SIGNAL_POWER Computes average signal power.
% Inputs: x is a real or complex sample vector.
% Returns: p is signal_energy(x) divided by sample count.
% Algorithm: divide summed squared magnitudes by length(x).
    p = signal_energy(x) / length(x);
end
