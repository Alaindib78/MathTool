% Calculer le PGCD
function c = pgcd(a, b)
    if a == b
        c = a
    elseif a > b
        c = pgcd(a - b, b);
    else 
        c = pgcd(a, b - a);
    end
end



print(pgcd(55, 21));