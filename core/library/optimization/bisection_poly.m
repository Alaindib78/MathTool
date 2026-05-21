function result = bisection_poly(coeffs, left, right, tol, maxIter)
% BISECTION_POLY Finds a real polynomial root in a sign-changing interval.
% Inputs: coeffs are polynomial coefficients, left/right bracket the root.
% Returns: result is [root, f(root), iterations].
% Algorithm: repeatedly bisect the interval and keep the sign-changing half.
    fleft = polyval(coeffs, left);
    fright = polyval(coeffs, right);

    if fleft * fright > 0
        error("bisection_poly: interval must bracket a sign change");
    end

    iter = 0;
    mid = (left + right) / 2;
    fmid = polyval(coeffs, mid);

    while iter < maxIter && abs(right - left) / 2 > tol
        mid = (left + right) / 2;
        fmid = polyval(coeffs, mid);

        if fmid == 0
            result = [mid, fmid, iter];
            return;
        end

        if fleft * fmid < 0
            right = mid;
            fright = fmid;
        else
            left = mid;
            fleft = fmid;
        end

        iter = iter + 1;
    end

    result = [mid, fmid, iter];
end
