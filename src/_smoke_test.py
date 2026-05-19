"""Prueba rápida de API + solver (sin GUI)."""

from __future__ import annotations

from src.api import SudokuAPI
from src.solver import BacktrackingSolver


def run_smoke_test() -> None:
    api = SudokuAPI()
    solver = BacktrackingSolver()
    puzzle = api.fetch_board("easy")
    assert len(puzzle) == 9 and all(len(row) == 9 for row in puzzle)
    solution = solver.solve(puzzle)
    assert solution is not None
    for row in solution:
        assert all(1 <= v <= 9 for v in row)
    print("Smoke test OK: puzzle fetched and solved.")


if __name__ == "__main__":
    run_smoke_test()
