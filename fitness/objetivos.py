#gestion de objetivos

from datetime import datetime

from fitness import db
from fitness.voz import hablar


def establecer_objetivo(objetivo):
    """Registra un nuevo objetivo del usuario."""
    conexion = db.conectar()
    cursor = conexion.cursor()

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute(
        "INSERT INTO objetivos (objetivo, fecha) VALUES (?, ?)",
        (objetivo, fecha),
    )

    conexion.commit()
    conexion.close()

    hablar(f"Tu objetivo ha sido registrado: {objetivo}")


def consultar_objetivo():
    """Informa el objetivo actual (el ultimo registrado)."""
    conexion = db.conectar()
    cursor = conexion.cursor()

    cursor.execute(
        "SELECT objetivo FROM objetivos ORDER BY id DESC LIMIT 1"
    )
    fila = cursor.fetchone()
    conexion.close()

    if fila:
        hablar(f"Tu objetivo actual es: {fila[0]}")
    else:
        hablar("Todavia no tienes un objetivo registrado.")
