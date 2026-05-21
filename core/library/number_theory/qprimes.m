function primes = qprimes(n)
    % qprimes(n) returns all prime numbers up to n using the 
    % Sieve of Eratosthenes algorithm.
    
    if n < 2
        primes = [];
        return;
    end
    
    % Initialize sieve array (true means potentially prime)
    sieve = true(1, n);
    sieve(1, 1) = false; % 1 is not prime
    
    % Sieve of Eratosthenes
    limit = floor(sqrt(n))
    for idx = 2:limit
        if sieve(1, idx)
            mult = idx;
            while mult*idx <= n
            	% Mark all multiples of idx as not prime
            	sieve(1, idx*mult) = false;
            	mult = mult + 1
            end
        end
    end
    
    % Extract indices where sieve is true
    primes = find(sieve);
end