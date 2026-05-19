"""Persistencia de estadísticas de partidas con sqlite3."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PartidaRecord:
    """Registro de una partida almacenada."""

    id: int
    dificultad: str
    tiempo_segundos: int
    fallos: int
    autocompletado: bool
    fecha: str


class DatabaseManager:
    """Gestiona la base de datos local sudoku_stats.db."""

    def __init__(self, db_path: Path | None = None) -> None:
        if db_path is None:
            db_path = Path(__file__).resolve().parent.parent / "sudoku_stats.db"
        self._db_path = db_path
        self.ensure_schema()

    def ensure_schema(self) -> None:
        """Crea la tabla partidas si no existe y aplica migraciones."""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS partidas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dificultad TEXT NOT NULL,
                    tiempo_segundos INTEGER NOT NULL,
                    fallos INTEGER NOT NULL,
                    autocompletado INTEGER NOT NULL DEFAULT 0,
                    fecha TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            columns = {
                row[1] for row in conn.execute("PRAGMA table_info(partidas)").fetchall()
            }
            if "autocompletado" not in columns:
                conn.execute(
                    """
                    ALTER TABLE partidas
                    ADD COLUMN autocompletado INTEGER NOT NULL DEFAULT 0
                    """
                )
            conn.commit()

    def insert_partida(
        self,
        dificultad: str,
        tiempo_segundos: int,
        fallos: int,
        autocompletado: bool = False,
    ) -> None:
        """
        Inserta una partida completada.

        Args:
            dificultad: Nivel jugado (easy, medium, hard).
            tiempo_segundos: Duración en segundos.
            fallos: Número de errores cometidos.
            autocompletado: True si terminó con "Mostrar Solución".
        """
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                INSERT INTO partidas (dificultad, tiempo_segundos, fallos, autocompletado)
                VALUES (?, ?, ?, ?)
                """,
                (dificultad, tiempo_segundos, fallos, int(autocompletado)),
            )
            conn.commit()

    def get_all_partidas(self) -> list[PartidaRecord]:
        """Devuelve todas las partidas, de la más reciente a la más antigua."""
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT id, dificultad, tiempo_segundos, fallos, autocompletado, fecha
                FROM partidas
                ORDER BY id DESC
                """
            ).fetchall()
        return [
            PartidaRecord(
                id=row["id"],
                dificultad=row["dificultad"],
                tiempo_segundos=row["tiempo_segundos"],
                fallos=row["fallos"],
                autocompletado=bool(row["autocompletado"]),
                fecha=row["fecha"] or "",
            )
            for row in rows
        ]
