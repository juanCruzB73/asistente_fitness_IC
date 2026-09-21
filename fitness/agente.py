#compresion de comandos

from fitness import objetivos
from fitness.voz import hablar

# Frases que indican que el usuario quiere "fijar" un objetivo.
_DISPARADORES_SET = ("quiero", "mi objetivo es", "objetivo:", "meta es")


def procesar_comando(comando):
    #Recibe texto del usuario y ejecuta la accion correspondiente.
    texto = comando.lower().strip()

    if "objetivo" in texto or "quiero" in texto or "meta" in texto:
        _manejar_objetivo(comando, texto)

    elif "rutina" in texto:
        hablar("La gestion de rutinas se implementa en el Bloque 3.")

    elif "historial" in texto:
        hablar("La consulta de historial se implementa en el Bloque 5.")

    elif "progreso" in texto:
        hablar("El analisis de progreso se implementa en el Bloque 6.")

    else:
        hablar(
            "No entendi el comando. Puedes preguntarme por tu objetivo, "
            "rutina o progreso. Escribe 'ayuda' para ver los comandos."
        )


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
