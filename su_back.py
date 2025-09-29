#!/usr/bin/env python3

import sys

class SudokuBacktracking:
    def __init__(self, grid):
        self.grid = grid

    def find_empty(self):
        """Find the next empty cell (row, col), or None if solved."""
        for r in range(9):
            for c in range(9):
                if self.grid[r][c] == 0:
                    return r, c
        return None

    def is_valid(self, row, col, num):
        """Check if placing num at (row, col) is valid."""

        # Row check
        if num in self.grid[row]:
            return False

        # Column check
        if num in (self.grid[i][col] for i in range(9)):
            return False

        # 3x3 block check
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(start_row, start_row + 3):
            for j in range(start_col, start_col + 3):
                if self.grid[i][j] == num:
                    return False

        return True

    def solve(self):
        """Solve Sudoku via backtracking with pruning."""
        empty = self.find_empty()
        if not empty:
            return True  # solved
        row, col = empty

        for num in range(1, 10):  # try digits 1-9
            if self.is_valid(row, col, num):
                self.grid[row][col] = num  # place number

                if self.solve():  # recurse
                    return True

                self.grid[row][col] = 0  # undo if dead end

        return False

    def print_grid(self):
        for r in range(9):
            row = ""
            for c in range(9):
                row += str(self.grid[r][c]) if self.grid[r][c] != 0 else "."
                if c in (2, 5):
                    row += " | "
                else:
                    row += " "
            print(row)
            if r in (2, 5):
                print("-" * 21)


def read_puzzle_from_txt(path):
    grid = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.replace(",", " ").split()
            row = []
            for p in parts:
                if p in ("0", ".", ""):
                    row.append(0)
                else:
                    row.append(int(p))
            grid.append(row)
    return grid


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python su_back.py test.txt")
        sys.exit(1)

    path = sys.argv[1]
    grid = read_puzzle_from_txt(path)

    solver = SudokuBacktracking(grid)
    if solver.solve():
        solver.print_grid()
    else:
        print("No solution exists")
