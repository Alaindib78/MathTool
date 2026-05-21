function i = rl_current_rise(v, r, l, t)
% RL_CURRENT_RISE Computes current rise in a series RL step.
% Inputs: v is applied voltage, r is resistance, l is inductance, t is time.
% Returns: i is current at time t.
% Algorithm: evaluate (V/R)*(1-exp(-R*t/L)).
    if r == 0 || l <= 0
        error("rl_current_rise: resistance must be nonzero and inductance positive");
    end

    i = (v / r) * (1 - exp(-r * t / l));
end
