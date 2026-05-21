function y = first_order_lowpass(x, dt, tau)
% FIRST_ORDER_LOWPASS Applies a discrete first-order low-pass filter.
% Inputs: x is a sample vector, dt is sample time, tau is the time constant.
% Returns: y is the filtered signal.
% Algorithm: use alpha=dt/(tau+dt) and exponential recursion.
    if tau <= 0 || dt <= 0
        error("first_order_lowpass: dt and tau must be positive");
    end

    alpha = dt / (tau + dt);
    y = exponential_smooth(x, alpha);
end
