function x = inv_db20(db)
% INV_DB20 Converts decibels to an amplitude ratio.
% Inputs: db is decibels for an amplitude quantity.
% Returns: x is 10^(db/20).
% Algorithm: evaluate the inverse of 20*log10(x).
    x = 10 ^ (db / 20);
end
