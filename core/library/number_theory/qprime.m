function result = qprime(n)
    % qprime(n) returns true if n is a prime number, false otherwise.
    % This implementation uses the Trial Division algorithm with 6k +/- 1 optimization.

    % 1. Handle non-positive numbers, 0, and 1 (not prime)
    if n <= 1
        result = false;
        return;
    end

    % 2. Handle the only even prime (2) and the first odd prime (3)
    if n <= 3
        result = true;
        return;
    end

    % 3. Eliminate multiples of 2 and 3 immediately
    if mod(n, 2) == 0 || mod(n, 3) == 0
        result = false;
        return;
    end

    % 4. Check for factors from 5 up to sqrt(n)
    % All primes greater than 3 are of the form 6k +/- 1.
    % We increment by 6 and check i (6k-1) and i+2 (6k+1).
    limit = floor(sqrt(n));
    for i = 5:6:limit
        if mod(n, i) == 0 || mod(n, i + 2) == 0
            result = false;
            return;
        end
    end

    % If no divisors were found, the number is prime
    result = true;
end