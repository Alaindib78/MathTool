function result = golden_section_poly(coeffs, left, right, tol, maxIter)
% GOLDEN_SECTION_POLY Minimizes a polynomial on a scalar interval.
% Inputs: coeffs are polynomial coefficients, left/right are bounds.
% Returns: result is [xmin, fmin, iterations].
% Algorithm: use golden-section interval reduction for unimodal functions.
    if left >= right
        error("golden_section_poly: left must be smaller than right");
    end

    gr = (sqrt(5) - 1) / 2;
    c = right - gr * (right - left);
    d = left + gr * (right - left);
    fc = polyval(coeffs, c);
    fd = polyval(coeffs, d);
    iter = 0;

    while iter < maxIter && abs(right - left) > tol
        if fc < fd
            right = d;
            d = c;
            fd = fc;
            c = right - gr * (right - left);
            fc = polyval(coeffs, c);
        else
            left = c;
            c = d;
            fc = fd;
            d = left + gr * (right - left);
            fd = polyval(coeffs, d);
        end

        iter = iter + 1;
    end

    xmin = (left + right) / 2;
    result = [xmin, polyval(coeffs, xmin), iter];
end
