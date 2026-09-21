"""Registro de ejercicios realizados en SQLite."""

from contextlib import closing
from datetime import datetime
import math

from fitness import db
from fitness.voz import hablar


def registrar_ejercicio(ejercicio, peso, repeticiones, series):
    """Valida y guarda un ejercicio; devuelve True si se pudo registrar.

    El peso se expresa en kg y puede ser cero para ejercicios sin carga.
    Las repeticiones y las series deben ser enteros positivos.
    """
    if not isinstance(ejercicio, str) or not ejercicio.strip():
        hablar("Indica el nombre del ejercicio.")
        return False

    try:
        if isinstance(peso, bool):
            raise ValueError
        peso = float(str(peso).strip().replace(",", "."))
        if not math.isfinite(peso) or peso < 0:
            raise ValueError
    except (ValueError, TypeError, OverflowError):
        hablar("El peso debe ser un número finito mayor o igual a cero, en kg.")
        return False

    try:
        repeticiones = int(str(repeticiones).strip())
        series = int(str(series).strip())
        if not (0 < repeticiones <= 2**63 - 1 and 0 < series <= 2**63 - 1):
            raise ValueError
    except (ValueError, TypeError):
        hablar("Las repeticiones y las series deben ser enteros positivos válidos.")
        return False

    ejercicio = ejercicio.strip()
    fecha = datetime.now().isoformat(sep=" ", timespec="seconds")
    with closing(db.conectar()) as conexion:
        with conexion:
            conexion.execute(
                "INSERT INTO entrenamientos "
                "(ejercicio, peso, repeticiones, series, fecha) VALUES (?, ?, ?, ?, ?)",
                (ejercicio, peso, repeticiones, series, fecha),
            )

    hablar(
        f"Entrenamiento registrado: {ejercicio}, {peso:g} kg, "
        f"{series} series de {repeticiones} repeticiones. Fecha: {fecha}."
    )
    return True
