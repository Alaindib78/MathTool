function x = gradient_descent_quadratic(A, b, x0, alpha, tol, maxIter)
% GRADIENT_DESCENT_QUADRATIC Minimizes 0.5*x'*A*x - b'*x.
% Inputs: A is a matrix, b and x0 are column vectors, alpha is step size.
% Returns: x is the final iterate.
% Algorithm: iterate x = x - alpha*(A*x-b) until the step is small.
    x = x0;
    iter = 0;
    stepNorm = tol + 1;

    while iter < maxIter && stepNorm > tol
        grad = A * x - b;
        xnext = x - alpha * grad;
        stepNorm = vec_norm(xnext - x);
        x = xnext;
        iter = iter + 1;
    end
end
