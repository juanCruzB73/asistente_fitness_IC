"""Rutinas disponibles por grupo muscular."""

from fitness.voz import hablar

rutinas = {
    "pecho": ["Press de banca", "Press inclinado", "Aperturas con mancuernas"],
    "espalda": ["Jalón al pecho", "Remo con mancuerna", "Remo sentado"],
    "piernas": ["Sentadillas", "Prensa de piernas", "Elevaciones de talones"],
}


def mostrar_rutina(grupo_muscular):
    """Muestra los ejercicios del grupo o informa los grupos disponibles."""
    grupo = grupo_muscular.strip().lower()
    ejercicios = rutinas.get(grupo)
    disponibles = ", ".join(rutinas)

    if not ejercicios:
        if grupo:
            hablar(f"No existe una rutina para '{grupo}'. Grupos disponibles: {disponibles}.")
        else:
            hablar(f"Indica un grupo muscular. Grupos disponibles: {disponibles}.")
        return

    lista = "\n".join(
        f"  {numero}. {ejercicio}"
        for numero, ejercicio in enumerate(ejercicios, start=1)
    )
    hablar(f"Rutina de {grupo}:\n{lista}")
