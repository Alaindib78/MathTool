function y = exponential_smooth(x, alpha)
% EXPONENTIAL_SMOOTH Applies first-order exponential smoothing.
% Inputs: x is a sample vector, alpha is between 0 and 1.
% Returns: y is the smoothed signal.
% Algorithm: use y(i)=alpha*x(i)+(1-alpha)*y(i-1).
    n = length(x);

    if alpha < 0 || alpha > 1
        error("exponential_smooth: alpha must be between 0 and 1");
    end

    if n < 1
        error("exponential_smooth: at least one sample is required");
    end

    y = [x(1)];

    for i = 2:n
        next = alpha * x(i) + (1 - alpha) * y(i - 1);
        y = [y, next];
    end
end
