function e = signal_energy(x)
% SIGNAL_ENERGY Computes discrete signal energy.
% Inputs: x is a real or complex sample vector.
% Returns: e is sum(abs(x)^2).
% Algorithm: sum squared magnitudes over all samples.
    e = sum(abs(x) .* abs(x));
end
