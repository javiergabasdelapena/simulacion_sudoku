"""Aplicación principal y máquina de estados."""

from __future__ import annotations

from enum import Enum

import pygame

from src.api import APIError, SudokuAPI
from src.constants import FPS, WINDOW_HEIGHT, WINDOW_WIDTH
from src.database import DatabaseManager
from src.gui.game_screen import GameScreen
from src.gui.history_screen import HistoryScreen
from src.gui.menu_screen import MenuScreen
from src.gui.stats_screen import StatsScreen
from src.models import GameSession, Difficulty
from src.solver import BacktrackingSolver


class AppState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    LOADING = "loading"
    STATS = "stats"
    HISTORY = "history"


class SudokuApp:
    """Orquesta menú, juego, estadísticas y servicios."""

    MAX_FETCH_RETRIES = 3

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Sudoku")
        self.clock = pygame.time.Clock()

        self.api = SudokuAPI()
        self.solver = BacktrackingSolver()
        self.db = DatabaseManager()

        self.state = AppState.MENU
        self._loading_message = "Cargando puzzle..."

        self.menu = MenuScreen(
            on_difficulty_selected=self._start_game,
            on_show_history=self._show_history,
        )
        self.game = GameScreen(on_game_end=self._on_game_end)
        self.stats = StatsScreen(db=self.db, on_back_to_menu=self._back_to_menu)
        self.history = HistoryScreen(db=self.db, on_back=self._back_to_menu)

    def _start_game(self, difficulty: Difficulty) -> None:
        self.state = AppState.LOADING
        self._loading_message = "Cargando puzzle..."
        pygame.display.flip()
        self._load_and_start(difficulty)

    def _load_and_start(self, difficulty: Difficulty) -> None:
        for _attempt in range(self.MAX_FETCH_RETRIES):
            try:
                puzzle = self.api.fetch_board(difficulty)
                solution = self.solver.solve(puzzle)
                if solution is None:
                    continue
                session = GameSession.from_puzzle(puzzle, solution, difficulty)
                self.game.start_game(session)
                self.stats.reset()
                self.state = AppState.PLAYING
                return
            except APIError as exc:
                self.menu.set_error(str(exc))
                self.state = AppState.MENU
                return
        self.menu.set_error("No se pudo resolver el puzzle. Intenta de nuevo.")
        self.state = AppState.MENU

    def _on_game_end(self, elapsed_seconds: int, mistakes: int, autocompleted: bool) -> None:
        if self.game.session:
            self.stats.show_stats(
                self.game.session.difficulty,
                elapsed_seconds,
                mistakes,
                autocompleted=autocompleted,
            )
        self.state = AppState.STATS

    def _show_history(self) -> None:
        self.history.refresh()
        self.state = AppState.HISTORY

    def _back_to_menu(self) -> None:
        self.state = AppState.MENU
        self.menu.error_message = None

    def run(self) -> None:
        """Bucle principal de la aplicación."""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif self.state == AppState.MENU:
                    self.menu.handle_event(event)
                elif self.state == AppState.PLAYING:
                    self.game.handle_event(event)
                elif self.state == AppState.STATS:
                    self.stats.handle_event(event)
                elif self.state == AppState.HISTORY:
                    self.history.handle_event(event)

            if self.state == AppState.PLAYING:
                self.game.update()

            self._draw()
            self.clock.tick(FPS)

        pygame.quit()

    def _draw(self) -> None:
        if self.state == AppState.MENU:
            self.menu.draw(self.screen)
        elif self.state == AppState.LOADING:
            self.screen.fill((30, 30, 40))
            font = pygame.font.SysFont("consolas", 28)
            text = font.render(self._loading_message, True, (240, 240, 240))
            self.screen.blit(
                text, text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            )
        elif self.state == AppState.PLAYING:
            self.game.draw(self.screen)
        elif self.state == AppState.STATS:
            self.stats.draw(self.screen)
        elif self.state == AppState.HISTORY:
            self.history.draw(self.screen)
        pygame.display.flip()
