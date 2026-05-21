function mag = fft_magnitude(x)
% FFT_MAGNITUDE Computes the magnitude spectrum of a signal.
% Inputs: x is a sample vector.
% Returns: mag is abs(fft(x)).
% Algorithm: compute the FFT with the built-in fft and take magnitudes.
    mag = abs(fft(x));
end
