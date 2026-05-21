function db = db20(x)
% DB20 Converts an amplitude ratio to decibels.
% Inputs: x is an amplitude ratio.
% Returns: db is 20*log10(abs(x)).
% Algorithm: take absolute value, reject zero, and apply 20 log10.
    mag = abs(x);

    if mag == 0
        error("db20: magnitude must be nonzero");
    end

    db = 20 * log10(mag);
end
