% Nonlinear scalar root-finding examples
%
% This script exercises the MATLAB-like scalar solvers:
%   fzero
%   newtons_method
%   secant
%
% Run it from MathTool, then inspect the printed roots and workspace
% variables ending in _ok.

disp("Nonlinear scalar root finders");

% fzero with a sign-changing bracket.
f_cos = @(x) cos(x);
root_fzero_bracket = fzero(f_cos, [1 2]);
expected_fzero_bracket = pi / 2;
fzero_bracket_ok = abs(root_fzero_bracket - expected_fzero_bracket) < 1e-8;

disp("fzero bracket root:");
print(root_fzero_bracket);
print(fzero_bracket_ok);

% fzero with a scalar start. MathTool searches for a nearby sign change.
f_sin = @(x) sin(x);
root_fzero_scalar = fzero(f_sin, 3);
expected_fzero_scalar = pi;
fzero_scalar_ok = abs(root_fzero_scalar - expected_fzero_scalar) < 1e-8;

disp("fzero scalar-start root:");
print(root_fzero_scalar);
print(fzero_scalar_ok);

% fzero with a closure-captured parameter.
c = 2;
myfun = @(x,c) cos(c*x);
f_param = @(x) myfun(x,c);
root_fzero_param = fzero(f_param, 0.1);
expected_fzero_param = pi / 4;
fzero_param_ok = abs(root_fzero_param - expected_fzero_param) < 1e-8;

disp("fzero parameterized root:");
print(root_fzero_param);
print(fzero_param_ok);

% Newton-Raphson with an analytic derivative.
f_poly = @(x) x^3 - 2*x - 5;
df_poly = @(x) 3*x^2 - 2;
root_newton = newtons_method(f_poly, df_poly, 2);
expected_poly_root = 2.0945514815423265;
newton_ok = abs(root_newton - expected_poly_root) < 1e-8;

disp("newtons_method polynomial root:");
print(root_newton);
print(newton_ok);

% Newton-Raphson with options and iteration display.
f_fixed = @(x) cos(x) - x;
df_fixed = @(x) -sin(x) - 1;
root_newton_iter = newtons_method(f_fixed, df_fixed, 1, "TolX", 1e-12, "MaxIter", 50, "Display", "iter");
expected_fixed_root = 0.7390851332151607;
newton_iter_ok = abs(root_newton_iter - expected_fixed_root) < 1e-8;

disp("newtons_method fixed-point root:");
print(root_newton_iter);
print(newton_iter_ok);

% Secant method with two starting guesses.
root_secant = secant(f_poly, 1, 3);
secant_ok = abs(root_secant - expected_poly_root) < 1e-8;

disp("secant polynomial root:");
print(root_secant);
print(secant_ok);

% Secant method on cos(x) - x.
root_secant_fixed = secant(f_fixed, 0, 1);
secant_fixed_ok = abs(root_secant_fixed - expected_fixed_root) < 1e-8;

disp("secant fixed-point root:");
print(root_secant_fixed);
print(secant_fixed_ok);

% FullOutput returns a struct-like result with metadata.
result_newton = newtons_method(f_poly, df_poly, 2, "ReturnAll", true, "FullOutput", true);

disp("FullOutput root:");
print(result_newton.root);

disp("FullOutput fval:");
print(result_newton.fval);

disp("FullOutput iterations:");
print(result_newton.output.iterations);

disp("FullOutput function evaluations:");
print(result_newton.output.funcCount);

% Uncomment these lines one at a time to see structured failure messages.
% no_sign_change = fzero(@(x) x^2, [-1 1]);
% zero_derivative = newtons_method(@(x) x^3, @(x) 3*x^2, 0);
% bad_secant = secant(@(x) 1, 0, 1);

disp("Nonlinear root-finding example complete");
