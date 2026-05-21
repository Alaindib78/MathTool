function pa = psi_to_pascal(psi)
% PSI_TO_PASCAL Converts pressure from psi to pascals.
% Inputs: psi is pressure in pounds per square inch.
% Returns: pa is pressure in pascals.
% Algorithm: multiply by 6894.757293168.
    pa = psi * 6894.757293168;
end
