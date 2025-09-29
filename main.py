#!/usr/bin/env python3
from copy import deepcopy
import csv
import sys
from collections import deque

class SudokuCSP:
    def __init__(self, grid):
        # grid: 9x9 list of lists, 0 for empty
        assert len(grid) == 9 and all(len(row) == 9 for row in grid), "Grid must be 9x9"
        self.grid = grid
        self.cells = [(r, c) for r in range(9) for c in range(9)]
        self._build_peers()
        self.domains = {cell: set() for cell in self.cells}
        self._initialize_domains()

    def _build_peers(self):
        # peers: for each cell, set of other cells in same row/col/block
        self.peers = {}
        for r in range(9):
            for c in range(9):
                peers = set()
                # row
                peers.update([(r, j) for j in range(9) if j != c])
                # col
                peers.update([(i, c) for i in range(9) if i != r])
                # block
                br, bc = 3 * (r // 3), 3 * (c // 3)
                for i in range(br, br + 3):
                    for j in range(bc, bc + 3):
                        if (i, j) != (r, c):
                            peers.add((i, j))
                self.peers[(r, c)] = peers

    def _initialize_domains(self):
        for r in range(9):
            for c in range(9):
                val = self.grid[r][c]
                if val and 1 <= val <= 9:
                    self.domains[(r, c)] = {val}
                else:
                    # start with full domain then remove values seen in peers
                    used = {self.grid[i][j] for (i, j) in self.peers[(r, c)] if self.grid[i][j]}
                    self.domains[(r, c)] = set(range(1, 10)) - used

    # AC-3 algorithm
    def ac3(self, domains=None):
        if domains is None:
            domains = self.domains
        queue = deque()
        for xi in self.cells:
            for xj in self.peers[xi]:
                queue.append((xi, xj))
        while queue:
            xi, xj = queue.popleft()
            if self.revise(domains, xi, xj):
                if not domains[xi]:
                    return False
                for xk in self.peers[xi] - {xj}:
                    queue.append((xk, xi))
        return True

    def revise(self, domains, xi, xj):
        revised = False
        to_remove = set()
        for x in set(domains[xi]):
            # if x not supported by any value in domains[xj]
            if len(domains[xj]) == 1 and x in domains[xj]:
                to_remove.add(x)
        if to_remove:
            domains[xi] -= to_remove
            revised = True
        return revised

    def is_solved(self, domains=None):
        if domains is None:
            domains = self.domains
        return all(len(domains[cell]) == 1 for cell in self.cells)

    def select_unassigned_variable(self, domains):
        # MRV: variable with smallest domain >1
        mrv = [(len(domains[cell]), -len(self.peers[cell]), cell)
               for cell in self.cells if len(domains[cell]) > 1]
        if not mrv:
            return None
        mrv.sort()
        return mrv[0][2]

    def order_domain_values(self, var, domains):
        # LCV: prefer value that rules out fewest options in neighbors
        counts = []
        for val in domains[var]:
            count = 0
            for p in self.peers[var]:
                if val in domains[p]:
                    count += 1
            counts.append((count, val))
        counts.sort()
        return [v for (_, v) in counts]

    def assign_and_propagate(self, var, value, domains):
        # returns new_domains or None if inconsistency
        new_domains = deepcopy(domains)
        new_domains[var] = {value}
        # forward checking: remove value from peers
        for p in self.peers[var]:
            if value in new_domains[p]:
                new_domains[p] = set(new_domains[p]) - {value}
                if not new_domains[p]:
                    return None
        # run AC-3 on reduced domains to propagate further
        if not self.ac3(new_domains):
            return None
        return new_domains

    def backtrack(self, domains):
        if self.is_solved(domains):
            return domains
        var = self.select_unassigned_variable(domains)
        if var is None:
            return None
        for value in self.order_domain_values(var, domains):
            new_domains = self.assign_and_propagate(var, value, domains)
            if new_domains is None:
                continue
            result = self.backtrack(new_domains)
            if result is not None:
                return result
        return None

    def solve(self):
        # run initial AC-3 then backtrack
        domains = deepcopy(self.domains)
        if not self.ac3(domains):
            return None
        sol = self.backtrack(domains)
        if sol is None:
            return None
        # produce a solved grid
        solved_grid = [[0]*9 for _ in range(9)]
        for (r, c), vals in sol.items():
            if len(vals) == 1:
                solved_grid[r][c] = next(iter(vals))
            else:
                # should not happen
                solved_grid[r][c] = 0
        return solved_grid

# Utilities for I/O and printing

def read_puzzle_from_txt(path):
    grid = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # allow spaces, commas
            parts = [p for p in line.replace(',', ' ').split()]
            if len(parts) != 9:
                raise ValueError('Each line must have 9 values (use 0 or . for empty)')
            row = []
            for p in parts:
                if p in ('0', '.', ''):
                    row.append(0)
                else:
                    row.append(int(p))
            grid.append(row)
    if len(grid) != 9:
        raise ValueError('File must contain 9 non-empty rows')
    return grid

def read_puzzle_from_csv(path):
    grid = []
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if not any(cell.strip() for cell in row):
                continue
            if len(row) != 9:
                raise ValueError('Each CSV row must have 9 columns')
            parsed = []
            for p in row:
                p = p.strip()
                if p in ('', '0', '.'):
                    parsed.append(0)
                else:
                    parsed.append(int(p))
            grid.append(parsed)
    if len(grid) != 9:
        raise ValueError('CSV must contain 9 non-empty rows')
    return grid

def print_grid(grid):
    if grid is None:
        print('No solution found (unsolvable)')
        return
    for r in range(9):
        row = ''
        for c in range(9):
            row += str(grid[r][c]) if grid[r][c] != 0 else '.'
            if c in (2, 5):
                row += ' | '
            else:
                row += ' '
        print(row)
        if r in (2, 5):
            print('-'*21)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python sudoku_csp.py puzzle.txt|puzzle.csv')
        sys.exit(1)
    path = sys.argv[1]
    if path.lower().endswith('.csv'):
        grid = read_puzzle_from_csv(path)
    else:
        grid = read_puzzle_from_txt(path)
    solver = SudokuCSP(grid)
    solution = solver.solve()
    print_grid(solution)
