function q = poly_deflate_linear(c, root)
% POLY_DEFLATE_LINEAR Divides coefficients by the factor (x-root).
% Inputs: c is a descending-power coefficient vector, root is the known root.
% Returns: q is the quotient coefficient vector.
% Algorithm: perform synthetic division and discard the final remainder.
    n = length(c);

    if n < 2
        error("poly_deflate_linear: polynomial degree must be at least one");
    end

    q = [c(1)];
    carry = c(1);

    for i = 2:n - 1
        carry = c(i) + root * carry;
        q = [q, carry];
    end
end
