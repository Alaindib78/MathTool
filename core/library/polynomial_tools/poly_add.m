function s = poly_add(a, b)
% POLY_ADD Adds two descending-power polynomial coefficient vectors.
% Inputs: a and b are coefficient vectors.
% Returns: s is the aligned coefficient sum.
% Algorithm: left-pad the shorter vector with zeros while adding terms.
    na = length(a);
    nb = length(b);
    n = max([na, nb]);
    s = [];

    for i = 1:n
        value = 0;
        ia = i - (n - na);
        ib = i - (n - nb);

        if ia >= 1 && ia <= na
            value = value + a(ia);
        end

        if ib >= 1 && ib <= nb
            value = value + b(ib);
        end

        s = [s, value];
    end
end
