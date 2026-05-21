function n = safety_factor(strength, applied)
% SAFETY_FACTOR Computes factor of safety.
% Inputs: strength is allowable or failure load, applied is applied demand.
% Returns: n is strength/applied.
% Algorithm: divide capacity by demand.
    if applied == 0
        error("safety_factor: applied demand must be nonzero");
    end

    n = strength / applied;
end
