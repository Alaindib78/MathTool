function factors = prime_factors(n)
    % PRIME_FACTORS Returns the prime factorization of n as a vector.
    % Inputs: n is an integer greater than or equal to 2.
    % Returns: factors is a row vector containing prime factors of n.
    % Example: prime_factors(60) returns [2, 2, 3, 5].
    
    if n < 2
        error('prime_factors: input must be >= 2');
    end
    
    factors = [];
    divisor = 2;
    
    % Check divisibility starting from 2
    while divisor * divisor <= n
        while mod(n, divisor) == 0
            factors = [factors, divisor];
            n = n / divisor;
        end
        divisor = divisor + 1;
    end
    
    % If n is still greater than 1, it's a prime factor
    if n > 1
        factors = [factors, n];
    end
end
