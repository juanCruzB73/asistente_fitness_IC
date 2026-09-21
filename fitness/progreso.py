"""Comparación del peso registrado para un ejercicio a lo largo del tiempo."""

from contextlib import closing
from decimal import Decimal

from fitness import db
from fitness.voz import hablar


def analizar_progreso(ejercicio):
    """Compara primer y último peso por fecha, desempatando por id.

    Requiere la base inicializada y al menos dos registros del ejercicio.
    Informa la diferencia en kg o la falta de datos por hablar(); devuelve None.
    No compara volumen, series ni repeticiones.
    """
    if not isinstance(ejercicio, str) or not ejercicio.strip():
        hablar("Indica el ejercicio. Ejemplo: progreso de sentadillas")
        return

    ejercicio = ejercicio.strip()
    with closing(db.conectar()) as conexion:
        conexion.create_function("normalizar", 1, lambda valor: (valor or "").strip().casefold())
        registros = conexion.execute(
            "SELECT ejercicio, peso, fecha FROM entrenamientos "
            "WHERE normalizar(ejercicio) = ? ORDER BY fecha ASC, id ASC",
            (ejercicio.casefold(),),
        ).fetchall()

    if not registros:
        hablar(f"Todavía no tienes registros de '{ejercicio}'.")
        return
    if len(registros) < 2:
        hablar(f"Necesitas al menos dos registros de '{ejercicio}' para analizar el progreso.")
        return

    primero, ultimo = registros[0], registros[-1]
    # Evita residuos de coma flotante al restar pesos decimales.
    diferencia = Decimal(str(ultimo[1])) - Decimal(str(primero[1]))
    if diferencia > 0:
        cambio = f"El peso aumentó {diferencia:g} kg."
    elif diferencia < 0:
        cambio = f"El peso disminuyó {abs(diferencia):g} kg."
    else:
        cambio = "El peso se mantuvo igual."

    hablar(
        f"Progreso de {ultimo[0]}:\n"
        f"  Primer registro: {primero[1]:g} kg ({primero[2]}).\n"
        f"  Último registro: {ultimo[1]:g} kg ({ultimo[2]}).\n"
        f"  {cambio}"
    )
