function yq = lagrange_interp(x, y, xq)
% LAGRANGE_INTERP Evaluates the Lagrange interpolating polynomial.
% Inputs: x and y are sample vectors, xq is a scalar query point.
% Returns: yq is the polynomial interpolation estimate.
% Algorithm: sum y(i) times each Lagrange basis polynomial.
    n = length(x);
    yq = 0;

    for i = 1:n
        term = y(i);

        for j = 1:n
            if j ~= i
                term = term * (xq - x(j)) / (x(i) - x(j));
            end
        end

        yq = yq + term;
    end
end
