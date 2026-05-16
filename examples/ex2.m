% Matricial Calculations
M1 = [1 -1;
      2 2];
M2 = [1; -1];
M3 = eye(3);
TM1 = M1' * M2;

print(TM1);

iM = inv(M1);
print(iM);
print(M3);
print(M1 * iM);