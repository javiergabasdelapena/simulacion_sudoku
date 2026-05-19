"""Pantalla principal de juego."""

from __future__ import annotations

import time
from typing import Callable

import pygame

from src.constants import (
    BUTTON_HEIGHT,
    CELL_SIZE,
    COLOR_BG,
    COLOR_CELL_FIXED,
    COLOR_CELL_HIGHLIGHT,
    COLOR_CELL_SELECTED,
    COLOR_CELL_USER,
    COLOR_CELL_WRONG,
    COLOR_GRID,
    COLOR_GRID_THICK,
    COLOR_NOTES,
    COLOR_OVERLAY,
    COLOR_TEXT,
    FONT_CELL,
    FONT_MEDIUM,
    FONT_NOTES,
    FONT_SMALL,
    GRID_SIZE,
    GRID_X,
    GRID_Y,
    PAUSE_OVERLAY_ALPHA,
    STATS_BTN_HEIGHT,
    STATS_BTN_WIDTH,
    STATS_BTN_Y,
    TOOLBAR_Y,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from src.gui.widgets import Button, ToggleButton, format_time
from src.models import GameMode, GameSession


class GameScreen:
    """Bucle de juego: tablero, timer, pausa, modos y validación."""

    def __init__(
        self,
        on_game_end: Callable[[int, int, bool], None],
    ) -> None:
        self.on_game_end = on_game_end
        self.session: GameSession | None = None
        self._start_time: float = 0.0
        self._paused_at: float = 0.0
        self._total_paused: float = 0.0
        self._last_second: int = -1
        self._frozen_elapsed: int | None = None

        self._font_cell = pygame.font.SysFont("consolas", FONT_CELL, bold=True)
        self._font_notes = pygame.font.SysFont("consolas", FONT_NOTES)
        self._font_ui = pygame.font.SysFont("consolas", FONT_SMALL)
        self._font_timer = pygame.font.SysFont("consolas", FONT_SMALL + 2, bold=True)

        self._pause_btn = Button(
            pygame.Rect(WINDOW_WIDTH - 110, 8, 100, BUTTON_HEIGHT),
            "Pausa",
            callback=self._toggle_pause,
            font_size=FONT_SMALL,
        )
        self._resume_btn = Button(
            pygame.Rect((WINDOW_WIDTH - 180) // 2, WINDOW_HEIGHT // 2, 180, 44),
            "Reanudar",
            callback=self._toggle_pause,
        )
        btn_w = (WINDOW_WIDTH - GRID_X * 2 - 10) // 2
        self._mode_toggle = ToggleButton(
            pygame.Rect(GRID_X, TOOLBAR_Y, btn_w, BUTTON_HEIGHT),
            "Modo Notas",
            "Modo Entrada",
            is_on=False,
            on_toggle=self._on_mode_toggle,
        )
        self._solution_btn = Button(
            pygame.Rect(GRID_X + btn_w + 10, TOOLBAR_Y, btn_w, BUTTON_HEIGHT),
            "Mostrar Solución",
            callback=self._reveal_solution,
            font_size=FONT_SMALL,
        )
        self._stats_btn = Button(
            pygame.Rect(
                (WINDOW_WIDTH - STATS_BTN_WIDTH) // 2,
                STATS_BTN_Y,
                STATS_BTN_WIDTH,
                STATS_BTN_HEIGHT,
            ),
            "Ver estadísticas",
            callback=self._go_to_stats,
            font_size=FONT_SMALL,
        )

    def start_game(self, session: GameSession) -> None:
        """Inicia una nueva partida con la sesión dada."""
        self.session = session
        self._start_time = time.time()
        self._paused_at = 0.0
        self._total_paused = 0.0
        self._last_second = -1
        self._frozen_elapsed = None
        session.paused = False
        session.game_over = False
        session.autocompleted = False
        session.solution_revealed = False
        session.mistakes = 0
        session.mode = GameMode.ENTRY
        session.selected = None
        self._mode_toggle.is_on = False
        self._mode_toggle.text = self._mode_toggle.text_off
        self._pause_btn.text = "Pausa"

    def _toggle_pause(self) -> None:
        if not self.session or self.session.game_over or self.session.solution_revealed:
            return
        if self.session.paused:
            self._total_paused += time.time() - self._paused_at
            self.session.paused = False
        else:
            self._paused_at = time.time()
            self.session.paused = True

    def _on_mode_toggle(self, is_notes: bool) -> None:
        if self.session:
            self.session.mode = GameMode.NOTES if is_notes else GameMode.ENTRY

    def _reveal_solution(self) -> None:
        """Muestra la solución en el tablero; las estadísticas van en un paso aparte."""
        if not self.session or self.session.game_over or self.session.solution_revealed:
            return
        for row in range(9):
            for col in range(9):
                cell = self.session.cells[row][col]
                if not cell.is_fixed:
                    cell.value = self.session.solution[row][col]
                    cell.notes.clear()
                    cell.is_wrong = False
        self._frozen_elapsed = self._elapsed_seconds()
        self.session.elapsed_seconds = self._frozen_elapsed
        self.session.autocompleted = True
        self.session.solution_revealed = True
        self.session.game_over = True
        self.session.selected = None

    def _go_to_stats(self) -> None:
        """Pasa a la pantalla de estadísticas tras ver la solución."""
        if not self.session or not self.session.solution_revealed:
            return
        self.on_game_end(
            self._elapsed_seconds(),
            self.session.mistakes,
            autocompleted=True,
        )

    def _elapsed_seconds(self) -> int:
        if not self.session:
            return 0
        if self._frozen_elapsed is not None:
            return self._frozen_elapsed
        if self.session.paused:
            elapsed = self._paused_at - self._start_time - self._total_paused
        else:
            elapsed = time.time() - self._start_time - self._total_paused
        return max(0, int(elapsed))

    def cell_from_pos(self, mx: int, my: int) -> tuple[int, int] | None:
        """Convierte coordenadas de ratón a (fila, columna)."""
        if mx < GRID_X or my < GRID_Y:
            return None
        if mx >= GRID_X + GRID_SIZE or my >= GRID_Y + GRID_SIZE:
            return None
        col = (mx - GRID_X) // CELL_SIZE
        row = (my - GRID_Y) // CELL_SIZE
        return row, col

    def _handle_number_input(self, num: int) -> None:
        if not self.session or self.session.paused or self.session.game_over:
            return
        if self.session.selected is None:
            return
        row, col = self.session.selected
        cell = self.session.cells[row][col]
        if cell.is_fixed:
            return

        if self.session.mode == GameMode.NOTES:
            if num in cell.notes:
                cell.notes.discard(num)
            else:
                cell.notes.add(num)
            return

        cell.notes.clear()
        correct = self.session.solution[row][col]
        cell.value = num
        if num != correct:
            cell.is_wrong = True
            self.session.mistakes += 1
        else:
            cell.is_wrong = False

        if self.session.is_complete_and_correct():
            self.session.game_over = True
            self.on_game_end(
                self._elapsed_seconds(),
                self.session.mistakes,
                autocompleted=False,
            )

    def _handle_delete(self) -> None:
        if not self.session or self.session.paused or self.session.game_over:
            return
        if self.session.selected is None:
            return
        row, col = self.session.selected
        cell = self.session.cells[row][col]
        if cell.is_fixed:
            return
        if self.session.mode == GameMode.NOTES:
            cell.notes.clear()
        else:
            cell.value = 0
            cell.is_wrong = False
            cell.notes.clear()

    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.session:
            return

        if self.session.solution_revealed:
            self._stats_btn.handle_event(event)
            return

        if self.session.paused:
            self._resume_btn.handle_event(event)
            return

        self._pause_btn.handle_event(event)
        self._mode_toggle.handle_event(event)
        if not self.session.game_over:
            self._solution_btn.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = self.cell_from_pos(*event.pos)
            if pos:
                self.session.selected = pos

        if event.type == pygame.KEYDOWN:
            num = self._key_to_number(event.key)
            if num:
                self._handle_number_input(num)
            elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                self._handle_delete()

    @staticmethod
    def _key_to_number(key: int) -> int | None:
        if pygame.K_1 <= key <= pygame.K_9:
            return key - pygame.K_0
        if pygame.K_KP1 <= key <= pygame.K_KP9:
            return key - pygame.K_KP0
        return None

    def update(self) -> None:
        if not self.session or self.session.paused or self.session.game_over:
            return
        secs = self._elapsed_seconds()
        if secs != self._last_second:
            self._last_second = secs
            self.session.elapsed_seconds = secs

    def draw(self, surface: pygame.Surface) -> None:
        if not self.session:
            return
        surface.fill(COLOR_BG)
        self._draw_hud(surface)
        if self.session.solution_revealed:
            self._stats_btn.draw(surface)
        self._draw_grid(surface)
        self._draw_cells(surface)
        if not self.session.solution_revealed:
            self._pause_btn.draw(surface)
            if not self.session.game_over:
                self._mode_toggle.draw(surface)
                self._solution_btn.draw(surface)
        if self.session.paused:
            self._draw_pause_overlay(surface)

    def _draw_hud(self, surface: pygame.Surface) -> None:
        timer_text = format_time(self._elapsed_seconds())
        timer = self._font_timer.render(f"Tiempo: {timer_text}", True, COLOR_TEXT)
        surface.blit(timer, (GRID_X, 10))
        mistakes = self._font_ui.render(
            f"Fallos: {self.session.mistakes}", True, COLOR_CELL_WRONG
        )
        surface.blit(mistakes, (GRID_X, 32))
        if not self.session.solution_revealed:
            mode_label = "Notas" if self.session.mode == GameMode.NOTES else "Entrada"
            mode = self._font_ui.render(f"Modo: {mode_label}", True, COLOR_TEXT)
            surface.blit(mode, (GRID_X, 52))

    def _draw_grid(self, surface: pygame.Surface) -> None:
        for i in range(10):
            thickness = 3 if i % 3 == 0 else 1
            color = COLOR_GRID_THICK if i % 3 == 0 else COLOR_GRID
            x = GRID_X + i * CELL_SIZE
            y = GRID_Y + i * CELL_SIZE
            pygame.draw.line(surface, color, (x, GRID_Y), (x, GRID_Y + GRID_SIZE), thickness)
            pygame.draw.line(surface, color, (GRID_X, y), (GRID_X + GRID_SIZE, y), thickness)

    def _draw_cells(self, surface: pygame.Surface) -> None:
        assert self.session
        sel = self.session.selected
        for row in range(9):
            for col in range(9):
                rect = pygame.Rect(
                    GRID_X + col * CELL_SIZE,
                    GRID_Y + row * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                )
                if sel == (row, col):
                    pygame.draw.rect(surface, COLOR_CELL_SELECTED, rect)
                elif sel and (sel[0] == row or sel[1] == col):
                    pygame.draw.rect(surface, COLOR_CELL_HIGHLIGHT, rect)

                cell = self.session.cells[row][col]
                if cell.value != 0:
                    if cell.is_fixed:
                        color = COLOR_CELL_FIXED
                    elif cell.is_wrong:
                        color = COLOR_CELL_WRONG
                    else:
                        color = COLOR_CELL_USER
                    text = self._font_cell.render(str(cell.value), True, color)
                    surface.blit(text, text.get_rect(center=rect.center))
                elif cell.notes:
                    self._draw_notes(surface, rect, cell.notes)

    def _draw_notes(self, surface: pygame.Surface, rect: pygame.Rect, notes: set[int]) -> None:
        positions = {
            1: (0, 0), 2: (1, 0), 3: (2, 0),
            4: (0, 1), 5: (1, 1), 6: (2, 1),
            7: (0, 2), 8: (1, 2), 9: (2, 2),
        }
        sub_w = rect.width // 3
        sub_h = rect.height // 3
        for num in sorted(notes):
            cx, cy = positions[num]
            x = rect.x + cx * sub_w + sub_w // 2
            y = rect.y + cy * sub_h + sub_h // 2
            note = self._font_notes.render(str(num), True, COLOR_NOTES)
            surface.blit(note, note.get_rect(center=(x, y)))

    def _draw_pause_overlay(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((*COLOR_OVERLAY, PAUSE_OVERLAY_ALPHA))
        surface.blit(overlay, (0, 0))
        font = pygame.font.SysFont("consolas", FONT_MEDIUM, bold=True)
        paused = font.render("JUEGO EN PAUSA", True, COLOR_TEXT)
        surface.blit(paused, paused.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40)))
        self._resume_btn.draw(surface)
