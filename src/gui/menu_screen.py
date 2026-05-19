"""Pantalla del menú principal."""

from __future__ import annotations

from typing import Callable

import pygame

from src.constants import (
    COLOR_BG,
    DIFFICULTY_LABELS,
    FONT_LARGE,
    FONT_TITLE,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from src.gui.widgets import Button, draw_centered_text
from src.models import DIFFICULTIES, Difficulty


class MenuScreen:
    """Menú de selección de dificultad e historial."""

    def __init__(
        self,
        on_difficulty_selected: Callable[[Difficulty], None],
        on_show_history: Callable[[], None],
    ) -> None:
        self.on_difficulty_selected = on_difficulty_selected
        self.on_show_history = on_show_history
        self.error_message: str | None = None
        self._title_font = pygame.font.SysFont("consolas", FONT_TITLE, bold=True)
        self._subtitle_font = pygame.font.SysFont("consolas", FONT_LARGE)
        self._buttons: list[Button] = []
        self._build_buttons()

    def _build_buttons(self) -> None:
        self._buttons.clear()
        btn_w, btn_h = 280, 48
        center_x = (WINDOW_WIDTH - btn_w) // 2
        start_y = 200
        gap = 52

        for i, diff in enumerate(DIFFICULTIES):
            label = DIFFICULTY_LABELS.get(diff, diff.capitalize())
            rect = pygame.Rect(center_x, start_y + i * gap, btn_w, btn_h)
            self._buttons.append(
                Button(rect, label, callback=lambda d=diff: self._select(d))
            )

        history_rect = pygame.Rect(center_x, start_y + len(DIFFICULTIES) * gap + 20, btn_w, btn_h)
        self._buttons.append(
            Button(history_rect, "Ver historial", callback=self._open_history)
        )

    def _select(self, difficulty: Difficulty) -> None:
        self.error_message = None
        self.on_difficulty_selected(difficulty)

    def _open_history(self) -> None:
        self.error_message = None
        self.on_show_history()

    def set_error(self, message: str) -> None:
        """Muestra un mensaje de error en el menú."""
        self.error_message = message

    def handle_event(self, event: pygame.event.Event) -> None:
        for btn in self._buttons:
            btn.handle_event(event)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(COLOR_BG)
        draw_centered_text(surface, "SUDOKU", 70, self._title_font)
        draw_centered_text(surface, "Elige dificultad", 125, self._subtitle_font)
        for btn in self._buttons:
            btn.draw(surface)
        if self.error_message:
            err_font = pygame.font.SysFont("consolas", 22)
            err = err_font.render(self.error_message, True, (255, 100, 100))
            surface.blit(err, err.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 40)))
