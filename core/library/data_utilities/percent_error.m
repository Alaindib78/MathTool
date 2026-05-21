function p = percent_error(measured, reference)
% PERCENT_ERROR Computes percent error relative to a reference value.
% Inputs: measured is observed value, reference is expected value.
% Returns: p is 100*(measured-reference)/reference.
% Algorithm: divide signed error by reference and scale by 100.
    if reference == 0
        error("percent_error: reference must be nonzero");
    end

    p = 100 * (measured - reference) / reference;
end
