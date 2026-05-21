function p = fft_power_spectrum(x)
% FFT_POWER_SPECTRUM Computes a simple squared-magnitude FFT spectrum.
% Inputs: x is a sample vector.
% Returns: p contains abs(fft(x))^2 divided by length(x).
% Algorithm: compute the FFT, square each magnitude, and normalize by N.
    X = fft(x);
    n = length(X);
    p = [];

    for i = 1:n
        value = (abs(X(i)) ^ 2) / n;
        p = [p, value];
    end
end
