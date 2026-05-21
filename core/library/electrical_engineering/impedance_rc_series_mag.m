function z = impedance_rc_series_mag(r, c, f)
% IMPEDANCE_RC_SERIES_MAG Computes magnitude of series RC impedance.
% Inputs: r is resistance, c is capacitance, f is frequency.
% Returns: z is impedance magnitude in ohms.
% Algorithm: combine R and capacitive reactance by sqrt(R^2+Xc^2).
    xc = capacitive_reactance(c, f);
    z = sqrt(r ^ 2 + xc ^ 2);
end
