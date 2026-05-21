function k = spring_parallel(k1, k2)
% SPRING_PARALLEL Computes equivalent stiffness of two parallel springs.
% Inputs: k1 and k2 are spring stiffnesses.
% Returns: k is k1+k2.
% Algorithm: add the two stiffnesses.
    k = k1 + k2;
end
