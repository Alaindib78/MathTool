% Symbolic and numerical calculus examples

x = sym("x");

f = sin(x^2);
df = diff(f, x);
d4 = diff(x^6, x, 4);
F = int(x^2, x);
q_symbolic = int(sin(x), x, 0, pi);

print(df);
print(d4);
print(F);
print(q_symbolic);

A = [x x^2;
     sin(x) cos(x)];
dA = diff(A, x);
print(dA);

fun = @(t) exp(-t.^2);
q = integral(fun, 0, 1);
print(q);

q2 = integral2(@(u,v) u.^2 + v.^2, 0, 1, 0, 1);
print(q2);

ymax = @(u) 1 - u;
tri = integral2(@(u,v) u + v, 0, 1, 0, ymax);
print(tri);

Y = [1 4 9 16 25];
trap_area = trapz(Y);
print(trap_area);

grid_values = [1 2 3;
               4 5 6];
[FX, FY] = gradient(grid_values);
print(FX);
print(FY);
