function u = pid_response(kp, ki, kd, errorSignal, dt)
% PID_RESPONSE Computes parallel PID output for an error history.
% Inputs: kp, ki, kd are gains, errorSignal is a vector, dt is sample time.
% Returns: u is the controller output vector.
% Algorithm: accumulate integral error and use backward difference derivative.
    n = length(errorSignal);

    if dt <= 0
        error("pid_response: dt must be positive");
    end

    integral = 0;
    u = [];

    for i = 1:n
        integral = integral + errorSignal(i) * dt;

        if i == 1
            derivative = 0;
        else
            derivative = (errorSignal(i) - errorSignal(i - 1)) / dt;
        end

        value = kp * errorSignal(i) + ki * integral + kd * derivative;
        u = [u, value];
    end
end
