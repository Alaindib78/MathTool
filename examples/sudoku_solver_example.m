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
    row = 0;
    col = 0;
    found = false;

    for r = 1:9
        for c = 1:9
            if ~found
                if board(r, c) == 0
                    row = r;
                    col = c;
                    found = true;
                end
            end
        end
    end

    if ~found
        solved = board;
        return;
    end

    solved = zeros(9);

    for value = 1:9
        allowed = true;

        for c = 1:9
            if board(row, c) == value
                allowed = false;
            end
        end

        if allowed
            for r = 1:9
                if board(r, col) == value
                    allowed = false;
                end
            end
        end

        if allowed
            firstRow = floor((row - 1) / 3) * 3 + 1;
            firstCol = floor((col - 1) / 3) * 3 + 1;

            for r = firstRow:firstRow + 2
                for c = firstCol:firstCol + 2
                    if board(r, c) == value
                        allowed = false;
                    end
                end
            end
        end

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
