# Simulación Sudoku

Juego de Sudoku en Python con `pygame`, `requests` y `sqlite3`.

- El **tablero incompleto** se descarga desde la API pública [Sugoku](https://sugoku.onrender.com/).
- La **solución de referencia** se calcula internamente con un algoritmo de **backtracking** propio (no se usa la solución que pueda ofrecer la API).
- Las partidas terminadas se guardan en `sudoku_stats.db` (SQLite local) y pueden consultarse desde el menú **Ver historial**.

## Características

- Menú de dificultad: Fácil / Medio / Difícil.
- Temporizador, botón de pausa con overlay opaco y contador de fallos.
- Modos **Entrada** y **Notas** con toggle.
- Validación celda a celda contra la solución calculada por backtracking.
- Botón **Mostrar Solución** → muestra la solución y luego permite ver estadísticas.
- Pantalla de estadísticas con dificultad, tiempo, fallos y fecha.
- Historial de partidas con scroll.

## Requisitos

- Python 3.11 o 3.12 (recomendado; 3.14 puede dar problemas para compilar `pygame`).
- Dependencias en `requirements.txt`:
  - `pygame>=2.5.0`
  - `requests>=2.31.0`

## Instalación

```bash
pip install -r requirements.txt
```

En Windows, si tienes varias versiones de Python:

```powershell
py -3.12 -m pip install -r requirements.txt
```

## Ejecutar

```bash
python main.py
```

O en Windows con Python 3.12:

```powershell
py -3.12 main.py
```

## Estructura

```
src/
  api.py             # SudokuAPI (GET al tablero)
  solver.py          # BacktrackingSolver (recursivo)
  database.py        # DatabaseManager (SQLite)
  models.py          # Tipos: Board, GameMode, CellState, GameSession
  constants.py       # Colores y layout
  format_utils.py    # Formateo de fechas
  _smoke_test.py     # Prueba rápida sin GUI
  gui/
    app.py           # SudokuApp (máquina de estados)
    menu_screen.py
    game_screen.py
    stats_screen.py
    history_screen.py
    widgets.py
main.py              # Punto de entrada
```

## Prueba rápida sin interfaz

```bash
python -m src._smoke_test
```

Descarga un tablero `easy` y comprueba que el solver lo resuelve.
