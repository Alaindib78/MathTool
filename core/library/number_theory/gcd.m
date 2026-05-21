function result = gcd(a, b)
    % qgcd(a, b) returns the greatest common divisor of a and b
    % using the Euclidean algorithm.
    
    % Handle edge cases
    if a == 0 && b == 0
        error('qgcd: At least one input must be non-zero');
    end
    
    % Work with absolute values
    a = abs(a);
    b = abs(b);
    
    % Euclidean algorithm
    while b ~= 0
        temp = b;
        b = mod(a, b);
        a = temp;
    end
    
    result = a;
end