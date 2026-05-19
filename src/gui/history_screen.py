"""Pantalla de historial de partidas."""

from __future__ import annotations

from typing import Callable

import pygame

from src.constants import (
    COLOR_BG,
    COLOR_TEXT,
    DIFFICULTY_LABELS,
    FONT_LARGE,
    FONT_SMALL,
    FONT_TITLE,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from src.database import DatabaseManager, PartidaRecord
from src.format_utils import format_fecha
from src.gui.widgets import Button, draw_centered_text, format_time


class HistoryScreen:
    """Lista todas las partidas guardadas en la base de datos."""

    ROW_HEIGHT = 44
    LIST_TOP = 120
    LIST_BOTTOM = WINDOW_HEIGHT - 90
    MARGIN_X = 24

    def __init__(
        self,
        db: DatabaseManager,
        on_back: Callable[[], None],
    ) -> None:
        self.db = db
        self.on_back = on_back
        self._scroll_offset = 0
        self._partidas: list[PartidaRecord] = []
        self._title_font = pygame.font.SysFont("consolas", FONT_TITLE, bold=True)
        self._header_font = pygame.font.SysFont("consolas", FONT_SMALL, bold=True)
        self._row_font = pygame.font.SysFont("consolas", FONT_SMALL)
        self._empty_font = pygame.font.SysFont("consolas", FONT_LARGE)
        self._back_btn = Button(
            pygame.Rect((WINDOW_WIDTH - 260) // 2, WINDOW_HEIGHT - 55, 260, 44),
            "Volver al Menú",
            callback=on_back,
        )

    def _columns(self) -> dict[str, int]:
        """Posiciones X de columnas según el ancho de ventana."""
        x0 = self.MARGIN_X
        return {
            "dificultad": x0,
            "tiempo": x0 + 110,
            "fallos": x0 + 220,
            "resultado": x0 + 300,
            "fecha": x0 + 480,
        }

    def refresh(self) -> None:
        """Recarga las partidas desde la base de datos."""
        self._partidas = self.db.get_all_partidas()
        self._scroll_offset = 0

    def _visible_height(self) -> int:
        return self.LIST_BOTTOM - self.LIST_TOP

    def _max_scroll(self) -> int:
        total_height = len(self._partidas) * self.ROW_HEIGHT
        return max(0, total_height - self._visible_height())

    def handle_event(self, event: pygame.event.Event) -> None:
        self._back_btn.handle_event(event)
        if event.type == pygame.MOUSEWHEEL:
            self._scroll_offset -= event.y * 30
            self._scroll_offset = max(0, min(self._scroll_offset, self._max_scroll()))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self._scroll_offset = max(0, self._scroll_offset - self.ROW_HEIGHT)
            elif event.key == pygame.K_DOWN:
                self._scroll_offset = min(self._max_scroll(), self._scroll_offset + self.ROW_HEIGHT)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(COLOR_BG)
        draw_centered_text(surface, "Historial de partidas", 70, self._title_font)

        if not self._partidas:
            draw_centered_text(
                surface,
                "No hay partidas registradas",
                WINDOW_HEIGHT // 2 - 40,
                self._empty_font,
                (160, 160, 180),
            )
        else:
            self._draw_header(surface)
            self._draw_rows(surface)
            if self._max_scroll() > 0:
                hint = self._row_font.render(
                    "Usa la rueda del ratón o ↑↓ para desplazarte",
                    True,
                    (140, 140, 160),
                )
                surface.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 25)))

        self._back_btn.draw(surface)

    def _draw_header(self, surface: pygame.Surface) -> None:
        cols = self._columns()
        headers = [
            ("dificultad", "Dificultad"),
            ("tiempo", "Tiempo"),
            ("fallos", "Fallos"),
            ("resultado", "Resultado"),
            ("fecha", "Fecha"),
        ]
        for key, label in headers:
            text = self._header_font.render(label, True, COLOR_TEXT)
            surface.blit(text, (cols[key], self.LIST_TOP - 28))

    def _draw_rows(self, surface: pygame.Surface) -> None:
        clip = pygame.Rect(
            self.MARGIN_X,
            self.LIST_TOP,
            WINDOW_WIDTH - 2 * self.MARGIN_X,
            self._visible_height(),
        )
        surface.set_clip(clip)
        y = self.LIST_TOP - self._scroll_offset
        for i, partida in enumerate(self._partidas):
            if y + self.ROW_HEIGHT >= self.LIST_TOP and y < self.LIST_BOTTOM:
                self._draw_row(surface, partida, y, i % 2 == 0)
            y += self.ROW_HEIGHT
        surface.set_clip(None)

    def _draw_row(
        self,
        surface: pygame.Surface,
        partida: PartidaRecord,
        y: int,
        alt: bool,
    ) -> None:
        row_rect = pygame.Rect(
            self.MARGIN_X,
            y,
            WINDOW_WIDTH - 2 * self.MARGIN_X,
            self.ROW_HEIGHT - 4,
        )
        if alt:
            pygame.draw.rect(surface, (40, 45, 60), row_rect, border_radius=4)

        cols = self._columns()
        diff = DIFFICULTY_LABELS.get(partida.dificultad, partida.dificultad)
        tiempo = format_time(partida.tiempo_segundos)
        resultado = "Autocompletado" if partida.autocompletado else "Completado"
        fecha = format_fecha(partida.fecha)

        color_result = (255, 180, 100) if partida.autocompletado else (150, 220, 150)
        fields = [
            ("dificultad", diff, COLOR_TEXT),
            ("tiempo", tiempo, COLOR_TEXT),
            ("fallos", str(partida.fallos), COLOR_TEXT),
            ("resultado", resultado, color_result),
            ("fecha", fecha, (160, 160, 180)),
        ]
        for key, text, color in fields:
            rendered = self._row_font.render(text, True, color)
            surface.blit(rendered, (cols[key], y + 14))
