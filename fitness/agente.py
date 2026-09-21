#compresion de comandos

import re

from fitness import entrenamientos, objetivos, rutinas
from fitness.voz import hablar

# Frases que indican que el usuario quiere "fijar" un objetivo.
_DISPARADORES_SET = ("quiero", "mi objetivo es", "objetivo:", "meta es")


def procesar_comando(comando):
    #Recibe texto del usuario y ejecuta la accion correspondiente.
    texto = comando.lower().strip()

    if re.match(r"^(?:quiero\s+)?registrar\b", texto):
        _manejar_registro(comando)

    elif re.search(r"\brutina\b", texto):
        _manejar_rutina(texto)

    elif re.search(r"\bhistorial\b", texto):
        _manejar_historial(comando)

    elif "objetivo" in texto or "quiero" in texto or "meta" in texto:
        _manejar_objetivo(comando, texto)

    elif "progreso" in texto:
        hablar("El analisis de progreso se implementa en el Bloque 6.")

    else:
        hablar(
            "No entendi el comando. Puedes preguntarme por tu objetivo, "
            "rutina o progreso. Escribe 'ayuda' para ver los comandos."
        )


def _manejar_historial(comando):
    """Acepta 'historial de sentadillas' y 'Quiero ver mi historial de ...'."""
    ejercicio = re.split(r"\bhistorial\b", comando, maxsplit=1, flags=re.IGNORECASE)[1]
    ejercicio = ejercicio.strip(" :¿?¡!.,")
    ejercicio = re.sub(r"^de(?:\s+|$)", "", ejercicio, count=1, flags=re.IGNORECASE)
    entrenamientos.consultar_historial(ejercicio)


def _manejar_registro(comando):
    """Lee ejercicio, peso, repeticiones y series separados por punto y coma."""
    datos = re.sub(
        r"^(?:quiero\s+)?registrar\b\s*", "", comando.strip(),
        count=1, flags=re.IGNORECASE,
    ).split(";")
    if len(datos) != 4:
        hablar(
            "Usa: registrar ejercicio; peso en kg; repeticiones; series. "
            "Ejemplo: registrar sentadillas; 40; 10; 3"
        )
        return
    entrenamientos.registrar_ejercicio(*datos)


def _manejar_rutina(texto):
    """Extrae el grupo de comandos como 'Quiero ver mi rutina de piernas'."""
    grupo = re.split(r"\brutina\b", texto, maxsplit=1)[1].strip(" :¿?¡!.,")
    grupo = re.sub(r"^(?:de|para)(?:\s+|$)", "", grupo)
    grupo = re.sub(r"^(?:el|la|los|las)(?:\s+|$)", "", grupo)
    rutinas.mostrar_rutina(grupo)


def _manejar_objetivo(original, texto):
    #Distingue entre fijar un objetivo y consultarlo.
    quiere_fijar = any(d in texto for d in _DISPARADORES_SET)

    if quiere_fijar:
        objetivo = _extraer_objetivo(original, texto)
        if objetivo:
            objetivos.establecer_objetivo(objetivo)
        else:
            hablar("Cuentame cual es tu objetivo, por ejemplo: "
                   "'Quiero aumentar masa muscular'.")
    else:
        objetivos.consultar_objetivo()


def _extraer_objetivo(original, texto):
    #Quita la frase disparadora y devuelve el objetivo en si.
    for disparador in _DISPARADORES_SET:
        if disparador in texto:
            # Corta a partir del disparador sobre el texto original.
            inicio = texto.index(disparador) + len(disparador)
            return original[inicio:].strip(" :.")
    return original.strip()
