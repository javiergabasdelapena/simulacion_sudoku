"""Utilidades de formateo para la interfaz."""

from __future__ import annotations


def format_fecha(fecha: str) -> str:
    """Formatea la fecha de la BD como DD/MM/YYYY HH:MM."""
    if not fecha:
        return "-"
    try:
        normalized = fecha.replace("T", " ").strip()
        date_part, _, time_part = normalized.partition(" ")
        year, month, day = date_part.split("-")
        hour_min = time_part[:5] if time_part else ""
        if hour_min:
            return f"{day}/{month}/{year} {hour_min}"
        return f"{day}/{month}/{year}"
    except (ValueError, IndexError):
        return fecha[:19]
