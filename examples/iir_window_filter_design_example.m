% IIR filter design and window function examples
%
% This script exercises:
%   butter
%   cheby1
%   cheby2
%   ellip
%   hann
%   hamming
%   blackman
%   kaiser

disp("IIR filter design and window examples");

fs = 200;
t = 0:1/fs:2;

x_low = sin(2*pi*5*t);
x_mid = 0.8*sin(2*pi*30*t);
x_high = 0.4*sin(2*pi*70*t);
x = x_low + x_mid + x_high;

% Butterworth lowpass.
[b_butter, a_butter] = butter(6, 20/(fs/2));
y_butter = filtfilt(b_butter, a_butter, x);
butter_error = mean(abs(y_butter - x_low));

disp("Butterworth coefficient lengths:");
print([length(b_butter) length(a_butter)]);
disp("Butterworth lowpass error:");
print(butter_error);

% Chebyshev Type I bandpass for the middle component.
[b_cheby1, a_cheby1] = cheby1(5, 1, [20 40]/(fs/2), "bandpass");
y_cheby1 = filtfilt(b_cheby1, a_cheby1, x);
cheby1_error = mean(abs(y_cheby1 - x_mid));

disp("Chebyshev Type I bandpass error:");
print(cheby1_error);

% Chebyshev Type II highpass for the high-frequency component.
[b_cheby2, a_cheby2] = cheby2(5, 40, 50/(fs/2), "high");
y_cheby2 = filtfilt(b_cheby2, a_cheby2, x);
cheby2_error = mean(abs(y_cheby2 - x_high));

disp("Chebyshev Type II highpass error:");
print(cheby2_error);

% Elliptic bandstop removes the middle component.
[b_ellip, a_ellip] = ellip(5, 1, 50, [20 40]/(fs/2), "stop");
y_ellip = filtfilt(b_ellip, a_ellip, x);
x_without_mid = x_low + x_high;
ellip_error = mean(abs(y_ellip - x_without_mid));

disp("Elliptic bandstop error:");
print(ellip_error);

% Analog design form accepts the trailing "s" option.
[b_analog, a_analog] = butter(3, 20, "s");

disp("Analog Butterworth coefficient lengths:");
print([length(b_analog) length(a_analog)]);

% Window functions return column vectors.
w_hann = hann(32);
w_hamming = hamming(32, "periodic");
w_blackman = blackman(32, "symmetric", "single");
w_kaiser = kaiser(32, 8);

disp("Window sizes:");
print([
    size(w_hann, 1) size(w_hann, 2);
    size(w_hamming, 1) size(w_hamming, 2);
    size(w_blackman, 1) size(w_blackman, 2);
    size(w_kaiser, 1) size(w_kaiser, 2)
]);

disp("Window first and center samples:");
print([
    w_hann(1) w_hann(16);
    w_hamming(1) w_hamming(16);
    w_blackman(1) w_blackman(16);
    w_kaiser(1) w_kaiser(16)
]);

% Quick workspace checks.
butter_ok = butter_error < 0.2;
cheby1_ok = cheby1_error < 0.3;
cheby2_ok = cheby2_error < 0.25;
ellip_ok = ellip_error < 0.35;
windows_ok = size(w_hann, 1) == 32 && size(w_kaiser, 2) == 1;

disp("IIR/window checks:");
print([butter_ok cheby1_ok cheby2_ok ellip_ok windows_ok]);

figure();
plot(t, x, t, y_butter, t, y_cheby1, t, y_cheby2);
title("IIR filter design example");
xlabel("Time (s)");
ylabel("Amplitude");
legend("Original", "Butter lowpass", "Cheby1 bandpass", "Cheby2 highpass");
grid(true);

disp("IIR filter design and window examples complete");
