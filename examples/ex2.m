% Matricial Calculations
M1 = [1 -1;
      2 2];
M2 = [1; -1];
M3 = eye(3);
TM1 = M1' * M2;

disp(TM1);

iM = inv(M1);
disp(iM);
disp(M3);
disp(M1 * iM);