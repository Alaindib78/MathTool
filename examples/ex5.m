% Nicomachus's Theorem
function y = sum_cubes(n)
    sum = 0
    for i=1:n
        sum = sum + i^3;
    end
    y = sum;
end

function y = sum1(n)
    sum = 0
    for i=1:n
        sum = sum + i;
    end
    y = sum;
end

N = 20;
s1 =  sum_cubes(N);
s2 = (sum1(N))^2;

if s1 == s2
    disp("The theroem stands");
    disp(s1);
else
	disp("The theory is no good");
	disp(s1);
	disp(s2);
end

    