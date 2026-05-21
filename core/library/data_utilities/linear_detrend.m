function y = linear_detrend(t, x)
% LINEAR_DETREND Removes the least-squares straight-line trend from data.
% Inputs: t is sample coordinate vector, x is data vector.
% Returns: y is x minus the fitted line.
% Algorithm: fit line parameters and subtract m*t+b from x.
    params = linear_fit_params(t, x);
    trend = params(1) * t + params(2);
    y = x - trend;
end
