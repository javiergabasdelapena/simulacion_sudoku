"""Widgets reutilizables de la interfaz pygame."""

from __future__ import annotations

from typing import Callable

import pygame

from src.constants import (
    COLOR_BUTTON,
    COLOR_BUTTON_ACTIVE,
    COLOR_BUTTON_HOVER,
    COLOR_TEXT,
    FONT_MEDIUM,
    FONT_SMALL,
)


class Button:
    """Botón rectangular con hover y callback."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        callback: Callable[[], None] | None = None,
        font_size: int = FONT_SMALL,
    ) -> None:
        self.rect = rect
        self.text = text
        self.callback = callback
        self.font_size = font_size
        self.hovered = False
        self.active = False
        self._font: pygame.font.Font | None = None

    def _get_font(self) -> pygame.font.Font:
        if self._font is None:
            self._font = pygame.font.SysFont("consolas", self.font_size, bold=True)
        return self._font

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Procesa eventos. Devuelve True si se activó el botón."""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.active = True
                return True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.active and self.rect.collidepoint(event.pos):
                self.active = False
                if self.callback:
                    self.callback()
                return True
            self.active = False
        return False

    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja el botón."""
        if self.active:
            color = COLOR_BUTTON_ACTIVE
        elif self.hovered:
            color = COLOR_BUTTON_HOVER
        else:
            color = COLOR_BUTTON
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_TEXT, self.rect, width=2, border_radius=8)
        font = self._get_font()
        label = font.render(self.text, True, COLOR_TEXT)
        surface.blit(label, label.get_rect(center=self.rect.center))


class ToggleButton(Button):
    """Botón que alterna entre dos estados visuales."""

    def __init__(
        self,
        rect: pygame.Rect,
        text_on: str,
        text_off: str,
        is_on: bool = False,
        on_toggle: Callable[[bool], None] | None = None,
    ) -> None:
        super().__init__(rect, text_off, callback=None)
        self.text_on = text_on
        self.text_off = text_off
        self.is_on = is_on
        self.on_toggle = on_toggle

    def toggle(self) -> None:
        """Alterna el estado."""
        self.is_on = not self.is_on
        self.text = self.text_on if self.is_on else self.text_off
        if self.on_toggle:
            self.on_toggle(self.is_on)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.active and self.rect.collidepoint(event.pos):
                self.active = False
                self.toggle()
                return True
        return super().handle_event(event)


def format_time(seconds: int) -> str:
    """Formatea segundos como MM:SS."""
    minutes, secs = divmod(max(0, seconds), 60)
    return f"{minutes:02d}:{secs:02d}"


def draw_centered_text(
    surface: pygame.Surface,
    text: str,
    y: int,
    font: pygame.font.Font,
    color: tuple[int, int, int] = COLOR_TEXT,
) -> None:
    """Dibuja texto centrado horizontalmente."""
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(surface.get_width() // 2, y))
    surface.blit(rendered, rect)
