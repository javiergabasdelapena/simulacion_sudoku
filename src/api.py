"""Cliente HTTP para obtener puzzles de la API Sugoku."""

from __future__ import annotations

from typing import Any

import requests

from src.models import Board, Difficulty


class APIError(Exception):
    """Error al obtener o parsear un tablero desde la API."""


class SudokuAPI:
    """Obtiene tableros incompletos desde sugoku.onrender.com."""

    BASE_URL = "https://sugoku.onrender.com/board"

    def fetch_board(self, difficulty: Difficulty) -> Board:
        """
        Realiza GET y devuelve un tablero 9x9 normalizado.

        Args:
            difficulty: easy, medium o hard.

        Raises:
            APIError: Si falla la red, timeout o el formato es inválido.
        """
        try:
            response = requests.get(
                self.BASE_URL,
                params={"difficulty": difficulty},
                timeout=15,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise APIError(f"No se pudo conectar con la API: {exc}") from exc

        try:
            data: Any = response.json()
        except ValueError as exc:
            raise APIError("La respuesta de la API no es JSON válido.") from exc

        raw_board = self._extract_board(data)
        return self._normalize_board(raw_board)

    def _extract_board(self, data: Any) -> Any:
        """Extrae la matriz del payload JSON."""
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            if "board" in data:
                return data["board"]
            if "puzzle" in data:
                return data["puzzle"]
        raise APIError("Formato de respuesta desconocido: no se encontró el tablero.")

    def _normalize_board(self, raw: Any) -> Board:
        """Convierte el tablero crudo a list[list[int]] con 0 para vacíos."""
        if not isinstance(raw, list) or len(raw) != 9:
            raise APIError("El tablero debe tener 9 filas.")

        board: Board = []
        for row in raw:
            if not isinstance(row, list) or len(row) != 9:
                raise APIError("Cada fila debe tener 9 columnas.")
            normalized_row: list[int] = []
            for cell in row:
                normalized_row.append(self._normalize_cell(cell))
            board.append(normalized_row)

        for row in board:
            for val in row:
                if val < 0 or val > 9:
                    raise APIError(f"Valor de celda inválido: {val}")
        return board

    @staticmethod
    def _normalize_cell(cell: Any) -> int:
        """Normaliza una celda a entero 0-9."""
        if cell is None or cell == "" or cell == ".":
            return 0
        if isinstance(cell, int) and cell == 0:
            return 0
        if isinstance(cell, str):
            cell = cell.strip()
            if cell in ("", ".", "0"):
                return 0
            if not cell.isdigit():
                raise APIError(f"Celda no numérica: {cell!r}")
            return int(cell)
        if isinstance(cell, (int, float)):
            return int(cell)
        raise APIError(f"Tipo de celda no soportado: {type(cell)}")
