function result = uncertainty_product(x, sx, y, sy)
% UNCERTAINTY_PRODUCT Propagates independent uncertainty for z = x*y.
% Inputs: x and y are values, sx and sy are their standard uncertainties.
% Returns: result is [z, sz].
% Algorithm: use relative uncertainty propagation for a product.
    if x == 0 || y == 0
        error("uncertainty_product: nonzero nominal values are required");
    end

    z = x * y;
    sz = abs(z) * sqrt((sx / x) ^ 2 + (sy / y) ^ 2);
    result = [z, sz];
end
