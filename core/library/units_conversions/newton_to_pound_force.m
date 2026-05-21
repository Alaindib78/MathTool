function lbf = newton_to_pound_force(n)
% NEWTON_TO_POUND_FORCE Converts newtons to pound-force.
% Inputs: n is force in newtons.
% Returns: lbf is force in pounds-force.
% Algorithm: divide by 4.4482216152605.
    lbf = n / 4.4482216152605;
end
