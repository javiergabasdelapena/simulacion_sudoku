"""
Solucionador de Sudoku mediante BACKTRACKING RECURSIVO PURO.
============================================================

Este módulo implementa, sin ninguna librería externa de resolución, el
algoritmo clásico de "prueba y error con retroceso" que sigue al pie de la
letra el siguiente pseudocódigo:

    resolver_sudoku(tablero):
        si no hay más celdas vacías:
            devolver True (el Sudoku está resuelto)

        para cada número del 1 al 9:
            si el número es válido en la celda actual:
                poner el número en la celda            # AVANCE
                si resolver_sudoku(tablero):           # LLAMADA RECURSIVA
                    devolver True
                quitar el número (retroceder)          # RETROCESO / BACKTRACK

        devolver False (si no hay solución)

Reglas de validación aplicadas (Sudoku clásico 9x9):
    1. El número no debe repetirse en la misma FILA.
    2. El número no debe repetirse en la misma COLUMNA.
    3. El número no debe repetirse en la misma SUBCUADRÍCULA 3x3.

Posibles mejoras / heurísticas (extensión académica)
----------------------------------------------------
El algoritmo aquí implementado es correcto y completo, pero su rendimiento
puede mejorarse notablemente combinándolo con heurísticas de búsqueda. Estas
heurísticas NO cambian el resultado, solo reducen el número de nodos
explorados del árbol de decisiones:

* MRV (Minimum Remaining Values) - "celda más restringida primero":
  En lugar de elegir siempre la primera celda vacía recorriendo el tablero
  de arriba a abajo y de izquierda a derecha, se elige la celda vacía con
  MENOS números candidatos válidos. Si una celda solo admite un valor, ese
  valor se fija inmediatamente; si admite cero, podamos la rama ya.
  Resultado: el árbol se ramifica menos en cada nivel y el backtracking se
  dispara mucho antes ante caminos inviables.

* LCV (Least Constraining Value) - "valor menos restrictivo":
  Dada una celda elegida, probar primero el número que deje MÁS opciones
  abiertas a sus vecinos (fila, columna y caja). Así aumentamos la
  probabilidad de encontrar solución sin retroceder.

* Forward Checking:
  Mantener, para cada celda vacía, el conjunto de candidatos posibles. Al
  colocar un número en una celda, se eliminan los candidatos afectados en
  fila, columna y caja. Si alguna celda se queda sin candidatos, se
  retrocede inmediatamente (no hace falta llegar hasta ella probando).

* Propagación de restricciones (AC-3, Naked/Hidden Singles, etc.):
  Aplicar reglas lógicas humanas antes de cada paso de backtracking. Por
  ejemplo, si en una fila solo una celda puede contener el 7, se asigna
  directamente. Esto puede resolver Sudokus fáciles SIN entrar siquiera en
  recursión.

* Representación con bitmasks:
  Guardar los dígitos usados por fila, columna y caja como enteros con
  máscaras de bits. La comprobación de validez pasa de O(27) a O(1) por
  intento, acelerando el solver entre 5x y 20x.

En esta versión se prioriza la fidelidad al pseudocódigo del enunciado y la
legibilidad sobre la velocidad, por lo que dichas heurísticas se documentan
pero no se aplican.
"""

from __future__ import annotations

from copy import deepcopy

from src.models import Board


class BacktrackingSolver:
    """Resuelve tableros Sudoku 9x9 usando backtracking recursivo puro."""

    def solve(self, board: Board) -> Board | None:
        """
        Punto de entrada público del solver.

        Trabaja sobre una COPIA del tablero para no mutar el original que
        recibe el llamador (importante porque la GUI conserva el puzzle
        inicial para mostrar las pistas).

        Args:
            board: Matriz 9x9 con 0 en las celdas vacías.

        Returns:
            Una nueva matriz 9x9 totalmente resuelta, o ``None`` si el
            tablero de entrada no admite solución.
        """
        working = deepcopy(board)
        if self._resolver_sudoku(working):
            return working
        return None

    def _resolver_sudoku(self, board: Board) -> bool:
        """
        Implementación LITERAL del pseudocódigo de backtracking.

        Esta función es recursiva y opera "in-place" sobre ``board``:
        cuando avanza, escribe un número en una celda; cuando retrocede,
        vuelve a poner 0 en esa misma celda dejando el tablero exactamente
        como estaba antes del intento fallido.

        Devuelve ``True`` en cuanto encuentra una solución completa, lo que
        propaga el "éxito" hacia arriba por toda la pila de recursión.
        Devuelve ``False`` si en la celda actual ningún dígito 1-9 conduce a
        una solución: en ese caso quien la llamó tendrá que retroceder a su
        vez.
        """
        # ---- CASO BASE ----------------------------------------------------
        # "si no hay más celdas vacías: devolver True"
        # Si _buscar_celda_vacia devuelve None, significa que recorrimos el
        # tablero completo sin encontrar ningún 0 -> el Sudoku está resuelto.
        celda_vacia = self._buscar_celda_vacia(board)
        if celda_vacia is None:
            return True

        fila, columna = celda_vacia

        # ---- CASO RECURSIVO -----------------------------------------------
        # "para cada número del 1 al 9"
        for numero in range(1, 10):
            # "si el número es válido en la celda actual"
            if self._es_valido(board, fila, columna, numero):

                # === FASE 1: AVANCE ============================================
                # Colocamos tentativamente el número en la celda. A partir
                # de este momento el tablero "asume" que esta decisión es
                # buena y la recursión seguirá explorando con ella puesta.
                board[fila][columna] = numero

                # === FASE 2: LLAMADA RECURSIVA =================================
                # Pedimos al propio algoritmo que resuelva el sub-problema
                # resultante (el mismo tablero, pero con una celda menos
                # vacía). Si esa llamada devuelve True, hemos encontrado
                # una solución completa y propagamos el éxito hacia arriba
                # SIN borrar el número que acabamos de poner.
                if self._resolver_sudoku(board):
                    return True

                # === FASE 3: RETROCESO (BACKTRACKING) ==========================
                # Si llegamos aquí es porque la llamada recursiva devolvió
                # False: ningún camino que parta de "numero" en (fila,
                # columna) lleva a una solución. Limpiamos la celda
                # (volvemos a 0) para dejar el tablero exactamente como
                # estaba y probar con el siguiente candidato del bucle.
                board[fila][columna] = 0

        # Si ningún número del 1 al 9 funcionó en esta celda, devolvemos
        # False para que el nivel anterior de la recursión retroceda a su
        # vez. Si esto ocurre en la primera llamada, el Sudoku no tiene
        # solución.
        return False

    def _buscar_celda_vacia(self, board: Board) -> tuple[int, int] | None:
        """
        Devuelve la primera celda vacía leyendo el tablero de izquierda a
        derecha y de arriba a abajo, o ``None`` si ya está completo.

        Nota académica: aquí es exactamente donde se aplicaría la
        heurística MRV (ver docstring superior). Bastaría con recorrer
        todas las celdas vacías y devolver aquella con menos candidatos
        válidos, en lugar de devolver la primera que aparezca.
        """
        for fila in range(9):
            for columna in range(9):
                if board[fila][columna] == 0:
                    return fila, columna
        return None

    def _es_valido(self, board: Board, fila: int, columna: int, numero: int) -> bool:
        """
        Comprueba si ``numero`` se puede escribir en (fila, columna) sin
        violar ninguna de las tres reglas del Sudoku.
        """
        # Regla 1: el número no puede repetirse en la fila.
        for c in range(9):
            if board[fila][c] == numero:
                return False

        # Regla 2: el número no puede repetirse en la columna.
        for f in range(9):
            if board[f][columna] == numero:
                return False

        # Regla 3: el número no puede repetirse en la subcuadrícula 3x3.
        # Calculamos la esquina superior-izquierda de la caja a la que
        # pertenece la celda y recorremos sus 9 posiciones.
        inicio_fila = 3 * (fila // 3)
        inicio_columna = 3 * (columna // 3)
        for f in range(inicio_fila, inicio_fila + 3):
            for c in range(inicio_columna, inicio_columna + 3):
                if board[f][c] == numero:
                    return False

        return True
