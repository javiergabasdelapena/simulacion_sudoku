"""Tipos y modelos de datos del juego Sudoku."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal

Board = list[list[int]]
Difficulty = Literal["easy", "medium", "hard"]
DIFFICULTIES: tuple[Difficulty, ...] = ("easy", "medium", "hard")


class GameMode(Enum):
    """Modo de interacción con las celdas."""

    ENTRY = "entry"
    NOTES = "notes"


@dataclass
class CellState:
    """Estado de una celda editable por el jugador."""

    value: int = 0
    notes: set[int] = field(default_factory=set)
    is_fixed: bool = False
    is_wrong: bool = False


@dataclass
class GameSession:
    """Estado completo de una partida en curso."""

    puzzle: Board
    solution: Board
    cells: list[list[CellState]]
    difficulty: Difficulty
    mistakes: int = 0
    mode: GameMode = GameMode.ENTRY
    selected: tuple[int, int] | None = None
    paused: bool = False
    game_over: bool = False
    autocompleted: bool = False
    solution_revealed: bool = False
    elapsed_seconds: int = 0

    @classmethod
    def from_puzzle(cls, puzzle: Board, solution: Board, difficulty: Difficulty) -> GameSession:
        """Crea una sesión inicial a partir del puzzle y la solución."""
        cells: list[list[CellState]] = []
        for row in range(9):
            row_cells: list[CellState] = []
            for col in range(9):
                val = puzzle[row][col]
                row_cells.append(
                    CellState(
                        value=val,
                        is_fixed=val != 0,
                    )
                )
            cells.append(row_cells)
        return cls(puzzle=puzzle, solution=solution, cells=cells, difficulty=difficulty)

    def user_board(self) -> Board:
        """Devuelve el tablero actual del usuario como matriz 9x9."""
        return [[self.cells[r][c].value for c in range(9)] for r in range(9)]

    def is_complete_and_correct(self) -> bool:
        """True si todas las celdas coinciden con la solución."""
        for row in range(9):
            for col in range(9):
                if self.cells[row][col].value != self.solution[row][col]:
                    return False
        return True
