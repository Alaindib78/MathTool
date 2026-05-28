% =========================================================
% MathTool Sudoku Solver Example
% =========================================================
% Uses recursive backtracking to fill a 9-by-9 Sudoku grid.
% Empty cells are represented by 0.
% =========================================================

puzzle = [
    5 3 0 6 7 8 9 1 2;
    6 7 2 1 9 5 3 4 8;
    1 9 8 3 4 2 5 6 0;
    8 5 9 7 6 1 4 2 3;
    4 2 6 8 5 3 7 9 1;
    7 1 3 9 2 4 8 5 6;
    9 6 1 5 3 7 2 8 4;
    2 8 7 4 1 9 6 3 5;
    3 4 5 2 8 0 1 7 9
];

disp("Puzzle:");
disp(puzzle);

solution = solveSudoku(puzzle);

if sum(solution) == 0
    error("No Sudoku solution found");
end

disp("Solution:");
disp(solution);

expected = [
    5 3 4 6 7 8 9 1 2;
    6 7 2 1 9 5 3 4 8;
    1 9 8 3 4 2 5 6 7;
    8 5 9 7 6 1 4 2 3;
    4 2 6 8 5 3 7 9 1;
    7 1 3 9 2 4 8 5 6;
    9 6 1 5 3 7 2 8 4;
    2 8 7 4 1 9 6 3 5;
    3 4 5 2 8 6 1 7 9
];

matchesExpected = allclose(solution, expected);
fprintf("Matches expected solution: %d\n", matchesExpected);

function solved = solveSudoku(board)
    emptyCells = find(board == 0);

    if isempty(emptyCells)
        solved = board;
        return;
    end

    cellIndex = emptyCells(1);
    row = mod(cellIndex - 1, 9) + 1;
    col = floor((cellIndex - 1) / 9) + 1;

    solved = zeros(9);

    for value = 1:9
        rowValues = board(row, :);
        colValues = board(:, col);

        firstRow = floor((row - 1) / 3) * 3 + 1;
        firstCol = floor((col - 1) / 3) * 3 + 1;
        boxValues = board(firstRow:firstRow + 2, firstCol:firstCol + 2);

        allowed = ~any(rowValues == value) & ~any(colValues == value) & ~any(boxValues == value);

        if allowed
            candidate = board;
            candidate(row, col) = value;

            attempt = solveSudoku(candidate);

            if sum(attempt) > 0
                solved = attempt;
                return;
            end
        end
    end
end
