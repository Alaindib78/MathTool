function result = lcm(a, b)
    % lcm(a, b) returns the least common multiple of a and b
    % LCM(a,b) = |a*b| / GCD(a,b)
    
    if a == 0 || b == 0
        result = 0;
        return;
    end
    
    result = abs(a * b) / gcd(a, b);
    result = round(result); % Ensure integer result
end