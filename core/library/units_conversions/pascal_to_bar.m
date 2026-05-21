function bar = pascal_to_bar(pa)
% PASCAL_TO_BAR Converts pressure from pascals to bar.
% Inputs: pa is pressure in pascals.
% Returns: bar is pressure in bar.
% Algorithm: divide by 100000.
    bar = pa / 100000;
end
