function w = horsepower_to_watt(hp)
% HORSEPOWER_TO_WATT Converts mechanical horsepower to watts.
% Inputs: hp is mechanical horsepower.
% Returns: w is power in watts.
% Algorithm: multiply by 745.6998715822702.
    w = hp * 745.6998715822702;
end
