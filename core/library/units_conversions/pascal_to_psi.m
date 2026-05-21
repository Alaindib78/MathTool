function psi = pascal_to_psi(pa)
% PASCAL_TO_PSI Converts pressure from pascals to psi.
% Inputs: pa is pressure in pascals.
% Returns: psi is pressure in pounds per square inch.
% Algorithm: divide by 6894.757293168.
    psi = pa / 6894.757293168;
end
