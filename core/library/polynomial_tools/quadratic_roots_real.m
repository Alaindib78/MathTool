function r = quadratic_roots_real(a, b, c)
% QUADRATIC_ROOTS_REAL Computes real roots of a quadratic equation.
% Inputs: a, b, c define a*x^2 + b*x + c.
% Returns: r is [root1, root2].
% Algorithm: use the quadratic formula after checking the discriminant.
    if a == 0
        error("quadratic_roots_real: a must be nonzero");
    end

    disc = b * b - 4 * a * c;

    if disc < 0
        error("quadratic_roots_real: roots are complex");
    end

    r1 = (-b - sqrt(disc)) / (2 * a);
    r2 = (-b + sqrt(disc)) / (2 * a);
    r = [r1, r2];
end
