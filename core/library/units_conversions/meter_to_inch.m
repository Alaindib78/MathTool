function inch = meter_to_inch(m)
% METER_TO_INCH Converts meters to inches.
% Inputs: m is a length in meters.
% Returns: inch is length in inches.
% Algorithm: divide by the exact inch-to-meter factor.
    inch = m / 0.0254;
end
