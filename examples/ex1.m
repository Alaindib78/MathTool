function z = atan2(y, x)
    if abs(x) < 1*10^(-5)
        if y > 0
            z = pi/2
        else
            z = -pi/2
        end
    else
        z = atan(y/x)
    end
end

% First Tab
A = 9^(0.5);
B = cos(A);
disp(A);

C = atan2(1, 1);
disp(C);

