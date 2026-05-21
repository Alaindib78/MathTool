function e = rmse(predicted, actual)
% RMSE Computes root-mean-square error between two vectors.
% Inputs: predicted and actual are equal-length vectors.
% Returns: e is sqrt(mean((predicted-actual)^2)).
% Algorithm: compute residuals, average squared residuals, and take square root.
    r = predicted - actual;
    e = sqrt(mean(r .* r));
end
