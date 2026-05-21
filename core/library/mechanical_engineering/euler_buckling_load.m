function pcr = euler_buckling_load(E, I, K, length)
% EULER_BUCKLING_LOAD Computes Euler critical buckling load.
% Inputs: E is modulus, I is second moment, K is effective-length factor, length is column length.
% Returns: pcr is pi^2*E*I/(K*length)^2.
% Algorithm: evaluate the ideal pinned-column buckling expression with K.
    if K == 0 || length == 0
        error("euler_buckling_load: K and length must be nonzero");
    end

    pcr = pi ^ 2 * E * I / ((K * length) ^ 2);
end
