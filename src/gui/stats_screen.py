"""Pantalla de fin de partida y estadísticas."""

from __future__ import annotations

from datetime import datetime
from typing import Callable

import pygame

from src.constants import (
    COLOR_BG,
    COLOR_TEXT,
    DIFFICULTY_LABELS,
    FONT_LARGE,
    FONT_MEDIUM,
    FONT_TITLE,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from src.database import DatabaseManager
from src.format_utils import format_fecha
from src.gui.widgets import Button, draw_centered_text, format_time
from src.models import Difficulty


class StatsScreen:
    """Muestra resultados y persiste en base de datos."""

    def __init__(
        self,
        db: DatabaseManager,
        on_back_to_menu: Callable[[], None],
    ) -> None:
        self.db = db
        self.on_back_to_menu = on_back_to_menu
        self.difficulty: Difficulty = "easy"
        self.elapsed_seconds: int = 0
        self.mistakes: int = 0
        self.autocompleted: bool = False
        self.completed_date: str = ""
        self._saved = False
        self._title_font = pygame.font.SysFont("consolas", FONT_TITLE, bold=True)
        self._font = pygame.font.SysFont("consolas", FONT_MEDIUM)
        self._back_btn = Button(
            pygame.Rect((WINDOW_WIDTH - 260) // 2, WINDOW_HEIGHT - 70, 260, 44),
            "Volver al Menú Principal",
            callback=on_back_to_menu,
        )

    def show_stats(
        self,
        difficulty: Difficulty,
        elapsed_seconds: int,
        mistakes: int,
        autocompleted: bool = False,
    ) -> None:
        """Configura y guarda las estadísticas de la partida."""
        self.difficulty = difficulty
        self.elapsed_seconds = elapsed_seconds
        self.mistakes = mistakes
        self.autocompleted = autocompleted
        self.completed_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not self._saved:
            self.db.insert_partida(
                difficulty, elapsed_seconds, mistakes, autocompletado=autocompleted
            )
            self._saved = True

    def reset(self) -> None:
        """Reinicia el flag de guardado para la próxima partida."""
        self._saved = False
        self.autocompleted = False

    def handle_event(self, event: pygame.event.Event) -> None:
        self._back_btn.handle_event(event)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(COLOR_BG)
        if self.autocompleted:
            title = "Partida finalizada"
            subtitle_color = (255, 180, 100)
            subtitle = "Autocompletado con solución"
        else:
            title = "¡Partida completada!"
            subtitle_color = (150, 200, 150)
            subtitle = "¡Victoria!"

        draw_centered_text(surface, title, 100, self._title_font)
        draw_centered_text(surface, subtitle, 160, self._font, subtitle_color)

        diff_label = DIFFICULTY_LABELS.get(self.difficulty, self.difficulty)
        fecha_label = format_fecha(self.completed_date)
        lines = [
            f"Dificultad: {diff_label}",
            f"Tiempo: {format_time(self.elapsed_seconds)}",
            f"Fallos: {self.mistakes}",
            f"Fecha: {fecha_label}",
        ]
        y = 240
        for line in lines:
            draw_centered_text(surface, line, y, self._font)
            y += 48
        sub = pygame.font.SysFont("consolas", FONT_LARGE)
        draw_centered_text(surface, "Estadísticas guardadas", 450, sub, (150, 200, 150))
        self._back_btn.draw(surface)
