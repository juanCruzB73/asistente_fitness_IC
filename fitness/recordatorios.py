"""Recordatorios de la sesión actual, sin avisos automáticos."""

import re

from fitness.voz import hablar

recordatorios = []


def agregar_recordatorio(hora, mensaje):
    """Valida una hora HH:MM y agrega el mensaje a la lista de la sesión."""
    if not isinstance(hora, str) or not re.fullmatch(
        r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", hora.strip()
    ):
        hablar("Indica una hora válida en formato HH:MM, entre 00:00 y 23:59.")
        return False
    if not isinstance(mensaje, str) or not mensaje.strip():
        hablar("Indica el mensaje del recordatorio.")
        return False

    hora, mensaje = hora.strip(), mensaje.strip()
    recordatorios.append({"hora": hora, "mensaje": mensaje})
    hablar(f"Recordatorio agregado para las {hora}: {mensaje}")
    return True


def consultar_recordatorios():
    """Muestra los recordatorios de la sesión ordenados por hora."""
    if not recordatorios:
        hablar("Todavía no tienes recordatorios en esta sesión.")
        return
    lista = "\n".join(
        f"  {recordatorio['hora']}: {recordatorio['mensaje']}"
        for recordatorio in sorted(recordatorios, key=lambda item: item["hora"])
    )
    hablar(f"Recordatorios de esta sesión (sin avisos automáticos):\n{lista}")
