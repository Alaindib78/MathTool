function y = first_order_highpass(x, dt, tau)
% FIRST_ORDER_HIGHPASS Applies a discrete first-order high-pass filter.
% Inputs: x is a sample vector, dt is sample time, tau is the time constant.
% Returns: y is the filtered signal.
% Algorithm: use y(i)=alpha*(y(i-1)+x(i)-x(i-1)).
    n = length(x);

    if tau <= 0 || dt <= 0
        error("first_order_highpass: dt and tau must be positive");
    end

    if n < 1
        error("first_order_highpass: at least one sample is required");
    end

    alpha = tau / (tau + dt);
    y = [0];

    for i = 2:n
        next = alpha * (y(i - 1) + x(i) - x(i - 1));
        y = [y, next];
    end
end
