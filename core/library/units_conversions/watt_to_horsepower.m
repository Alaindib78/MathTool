function hp = watt_to_horsepower(w)
% WATT_TO_HORSEPOWER Converts watts to mechanical horsepower.
% Inputs: w is power in watts.
% Returns: hp is mechanical horsepower.
% Algorithm: divide by 745.6998715822702.
    hp = w / 745.6998715822702;
end
