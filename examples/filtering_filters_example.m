% Comprehensive digital filtering examples
%
% This script exercises MATLAB-style filtering helpers:
%   filter
%   filtfilt
%   fir1
%   designfilt
%   lowpass
%   highpass
%   bandpass
%   bandstop

disp("Digital filtering examples");

% Build a synthetic signal with low, mid, and high frequency components.
fs = 200;
t = 0:1/fs:2;

x_low = sin(2*pi*5*t);
x_mid = 0.7*sin(2*pi*25*t);
x_high = 0.4*sin(2*pi*60*t);
x = x_low + x_mid + x_high;

disp("Original signal length:");
print(length(x));

% Coefficient-form filter: simple moving average.
b_avg = [1 1 1 1 1] / 5;
a_avg = 1;
y_avg = filter(b_avg, a_avg, x);

disp("Moving-average filtered signal:");
print(y_avg(1:8));

% FIR design with fir1 and zero-phase filtering with filtfilt.
b_low_fir = fir1(40, 15, "low", "hamming", "SampleRate", fs);
y_low_fir = filtfilt(b_low_fir, 1, x);
low_fir_error = mean(abs(y_low_fir - x_low));

disp("FIR lowpass zero-phase error:");
print(low_fir_error);

% designfilt returns a digital filter object accepted by filter/filtfilt.
d_low = designfilt("lowpassfir", "FilterOrder", 40, "CutoffFrequency", 15, "SampleRate", fs);
y_low_design = filtfilt(d_low, x);
low_design_error = mean(abs(y_low_design - x_low));

disp("designfilt lowpass FIR error:");
print(low_design_error);

disp("designfilt numerator length:");
print(length(d_low.Numerator));

disp("designfilt denominator:");
print(d_low.Denominator);

% IIR designfilt example.
d_high = designfilt("highpassiir", "FilterOrder", 6, "HalfPowerFrequency", 40, "SampleRate", fs);
y_high_design = filtfilt(d_high, x);
high_design_error = mean(abs(y_high_design - x_high));

disp("designfilt highpass IIR error:");
print(high_design_error);

% Convenience lowpass and highpass functions.
y_low = lowpass(x, 15, fs, "FilterOrder", 6);
y_high = highpass(x, 40, fs, "FilterOrder", 6);

lowpass_error = mean(abs(y_low - x_low));
highpass_error = mean(abs(y_high - x_high));

disp("lowpass convenience error:");
print(lowpass_error);

disp("highpass convenience error:");
print(highpass_error);

% Bandpass isolates the middle component.
y_band = bandpass(x, [18 32], fs, "FilterOrder", 6);
bandpass_error = mean(abs(y_band - x_mid));

disp("bandpass convenience error:");
print(bandpass_error);

% Bandstop removes the middle component, leaving low + high components.
y_stop = bandstop(x, [18 32], fs, "FilterOrder", 6);
x_without_mid = x_low + x_high;
bandstop_error = mean(abs(y_stop - x_without_mid));

disp("bandstop convenience error:");
print(bandstop_error);

% FIR bandpass and bandstop designs through fir1.
b_band_fir = fir1(50, [18 32], "bandpass", "hamming", "SampleRate", fs);
y_band_fir = filtfilt(b_band_fir, 1, x);
band_fir_error = mean(abs(y_band_fir - x_mid));

b_stop_fir = fir1(50, [18 32], "stop", "hamming", "SampleRate", fs);
y_stop_fir = filtfilt(b_stop_fir, 1, x);
stop_fir_error = mean(abs(y_stop_fir - x_without_mid));

disp("fir1 bandpass error:");
print(band_fir_error);

disp("fir1 bandstop error:");
print(stop_fir_error);

% Matrix filtering: each column is filtered independently.
X = [x_low' x_mid' x_high'];
Y = lowpass(X, 15, fs, "FilterOrder", 6);
matrix_rows = size(Y, 1);
matrix_cols = size(Y, 2);

disp("Matrix lowpass output rows:");
print(matrix_rows);

disp("Matrix lowpass output columns:");
print(matrix_cols);

% Simple pass/fail checks for quick workspace inspection.
lowpass_ok = lowpass_error < 0.2;
highpass_ok = highpass_error < 0.2;
bandpass_ok = bandpass_error < 0.25;
bandstop_ok = bandstop_error < 0.25;
designfilt_ok = low_design_error < 0.2 && high_design_error < 0.2;
matrix_ok = matrix_rows == length(x) && matrix_cols == 3;

disp("Filtering checks:");
print([lowpass_ok highpass_ok bandpass_ok bandstop_ok designfilt_ok matrix_ok]);

% Plot a small visual comparison when running in the GUI.
figure();
plot(t, x, t, y_low, t, y_band, t, y_high);
title("Filtering example");
xlabel("Time (s)");
ylabel("Amplitude");
legend("Original", "Lowpass", "Bandpass", "Highpass");
grid(true);

disp("Digital filtering examples complete");
