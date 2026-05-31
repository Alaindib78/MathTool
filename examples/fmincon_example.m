% MATLAB-style constrained nonlinear optimization with fmincon
%
% This script exercises:
%   - unconstrained optimization
%   - bound constraints
%   - linear inequality and equality constraints
%   - nonlinear constraints
%   - optimoptions
%   - FullOutput
%   - problem-structure input

disp("fmincon examples");

% Unconstrained quadratic. Expected approximately [3 2].
quad = @(x) (x(1)-3)^2 + (x(2)-2)^2;
x0 = [0 0];
x_unconstrained = fmincon(quad, x0);

disp("Unconstrained quadratic:");
print(x_unconstrained);

% Bound-constrained quadratic. Expected approximately [1 1].
lb = [0 0];
ub = [1 1];
x_bounded = fmincon(quad, x0, [], [], [], [], lb, ub);

disp("Bound-constrained quadratic:");
print(x_bounded);

% Linear inequality: A*x' <= b.
rosen = @(x) 100*(x(2)-x(1)^2)^2 + (1-x(1))^2;
x0_rosen = [-1 2];
A = [1 2];
b = 1;
x_ineq = fmincon(rosen, x0_rosen, A, b);
ineq_value = A*x_ineq';

disp("Linear inequality solution:");
print(x_ineq);
disp("A*x' value:");
print(ineq_value);

% Linear inequality plus equality.
Aeq = [2 1];
beq = 1;
x_linear = fmincon(rosen, [0.5 0], A, b, Aeq, beq);
linear_ineq_value = A*x_linear';
linear_eq_value = Aeq*x_linear';

disp("Linear inequality/equality solution:");
print(x_linear);
disp("A*x' value:");
print(linear_ineq_value);
disp("Aeq*x' value:");
print(linear_eq_value);

% Nonlinear inequality c(x) <= 0 with bounds.
% Parentheses around the constraint expression keep the matrix literal
% parser unambiguous.
nonlcon = @(x) [((x(1)-1/3)^2 + (x(2)-1/3)^2 - (1/3)^2), []];
x_nonlin = fmincon(rosen, [0.25 0.25], [], [], [], [], [0 0.2], [0.5 0.8], nonlcon);
circle_value = (x_nonlin(1)-1/3)^2 + (x_nonlin(2)-1/3)^2 - (1/3)^2;

disp("Nonlinear constraint solution:");
print(x_nonlin);
disp("Circle constraint value:");
print(circle_value);

% Options object and iteration display.
options = optimoptions("fmincon", "Display", "iter", "Algorithm", "sqp", "MaxIterations", 100);
x_options = fmincon(rosen, [0 0], [], [], [], [], [], [], [], options);

disp("Options-based solution:");
print(x_options);

% FullOutput returns a struct-like OptimizationResult.
result = fmincon(quad, [0 0], "FullOutput", true, "Display", "final");

disp("FullOutput x:");
print(result.x);
disp("FullOutput fval:");
print(result.fval);
disp("FullOutput exitflag:");
print(result.exitflag);
disp("FullOutput iterations:");
print(result.output.iterations);
disp("FullOutput constraint violation:");
print(result.output.constrviolation);

% Problem-structure input.
problem.objective = quad;
problem.x0 = [0 0];
problem.lb = [0 0];
problem.ub = [10 10];
problem.solver = "fmincon";
problem.options = optimoptions("fmincon", "Display", "final");
x_problem = fmincon(problem);

disp("Problem-structure solution:");
print(x_problem);

% Uncomment these lines one at a time to inspect structured errors.
% bad_bounds = fmincon(@(x) x(1)^2, [0], [], [], [], [], [2], [1]);
% bad_objective = fmincon(@(x) [x(1), x(1)^2], [1]);

disp("fmincon examples complete");
