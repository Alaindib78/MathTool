function y = first_order_step_response(K, tau, t)
% FIRST_ORDER_STEP_RESPONSE Computes K*(1-exp(-t/tau)).
% Inputs: K is static gain, tau is time constant, t is a time vector.
% Returns: y is the first-order unit-step response.
% Algorithm: evaluate the analytic first-order response at each time.
    if tau <= 0
        error("first_order_step_response: tau must be positive");
    end

    n = length(t);
    y = [];

    for i = 1:n
        value = K * (1 - exp(-t(i) / tau));
        y = [y, value];
    end
end
