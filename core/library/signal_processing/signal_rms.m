function y = signal_rms(x)
% SIGNAL_RMS Computes the root-mean-square level of a signal.
% Inputs: x is a real or complex sample vector.
% Returns: y is sqrt(mean(abs(x)^2)).
% Algorithm: average squared magnitudes and take the square root.
    y = sqrt(mean(abs(x) .* abs(x)));
end
