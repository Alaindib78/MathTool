function tau = rc_time_constant(r, c)
% RC_TIME_CONSTANT Computes the time constant of an RC circuit.
% Inputs: r is resistance in ohms, c is capacitance in farads.
% Returns: tau is time constant in seconds.
% Algorithm: multiply R*C.
    tau = r * c;
end
