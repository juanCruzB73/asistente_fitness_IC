"""Interpreta los comandos de texto y los deriva al módulo correspondiente."""

import re

from fitness import entrenamientos, objetivos, progreso, recordatorios, rutinas
from fitness.voz import hablar

_CONSULTA = r"(?:quiero\s+)?(?:(?:ver|consultar|mostrar|muéstrame|muestrame)\s+)?"


def procesar_comando(comando):
    """Reconoce la intención al inicio sin interpretar palabras de los datos."""
    if not isinstance(comando, str) or not comando.strip():
        hablar("Escribe un comando. Usa 'ayuda' para ver las opciones.")
        return
    original = comando.strip().strip("¿?¡!.").strip()

    def coincide(patron, fuente=None):
        return re.fullmatch(patron, original if fuente is None else fuente, flags=re.IGNORECASE)

    registro = coincide(r"(?:quiero\s+)?registrar\b\s*(.*)")
    recordatorio = coincide(r"(?:quiero\s+)?(?:agregar\s+)?recordatorio\b\s*(.*)", comando.strip())
    fijar = coincide(
        r"(?:quiero\s+)?(?:(?:mi\s+)?(?:objetivo|meta)\s*(?:es\b|:)|"
        r"(?:fijar|establecer|cambiar)\s+(?:mi\s+)?(?:objetivo|meta)\b)\s*(.*)"
    )
    if registro:
        datos = registro[1].split(";")
        if len(datos) != 4:
            hablar("Usa: registrar ejercicio; peso en kg; repeticiones; series. "
                   "Ejemplo: registrar sentadillas; 40; 10; 3")
        else:
            entrenamientos.registrar_ejercicio(*datos)
        return
    if recordatorio:
        datos = recordatorio[1].split(";", maxsplit=1)
        if len(datos) != 2:
            hablar("Usa: recordatorio HH:MM; mensaje. "
                   "Ejemplo: recordatorio 18:30; Entrenar piernas")
        else:
            recordatorios.agregar_recordatorio(*datos)
        return
    if fijar:
        _establecer_objetivo(fijar[1])
        return
    if coincide(_CONSULTA + r"(?:mis\s+)?recordatorios"):
        recordatorios.consultar_recordatorios()
        return
    if coincide(_CONSULTA + r"(?:mi\s+)?(?:objetivo|meta)") or coincide(
        r"cu[aá]l\s+es\s+(?:mi\s+)?(?:objetivo|meta)"
    ):
        objetivos.consultar_objetivo()
        return

    consulta = coincide(_CONSULTA + r"(?:mi\s+)?(rutina|historial|progreso)\b\s*(.*)")
    if consulta:
        tipo, dato = consulta[1].lower(), consulta[2].strip(" :")
        dato = re.sub(r"^(?:de|para)(?:\s+|$)", "", dato, count=1, flags=re.IGNORECASE)
        if tipo == "rutina":
            dato = re.sub(r"^(?:el|la|los|las)(?:\s+|$)", "", dato, count=1, flags=re.IGNORECASE)
            rutinas.mostrar_rutina(dato)
        elif tipo == "historial":
            entrenamientos.consultar_historial(dato)
        else:
            progreso.analizar_progreso(dato)
        return

    grupo = coincide(_CONSULTA + r"(?:entrenar\s+)?(" + "|".join(map(re.escape, rutinas.rutinas)) + r")")
    if grupo:
        rutinas.mostrar_rutina(grupo[1].lower())
        return

    # Conserva la forma inicial de fijar objetivos sin capturar cualquier 'quiero'.
    deseo = coincide(r"quiero\s+((?:aumentar|ganar|perder|bajar|mejorar|mantener)\b.*)")
    if deseo:
        _establecer_objetivo(deseo[1])
        return
    hablar("No entendi el comando. Puedes consultar tu objetivo, rutina, historial "
           "o progreso, registrar ejercicios y gestionar recordatorios. "
           "Escribe 'ayuda' para ver los comandos.")


def _establecer_objetivo(objetivo):
    """Evita guardar objetivos vacíos tras un disparador explícito."""
    objetivo = objetivo.strip(" :.")
    if objetivo:
        objetivos.establecer_objetivo(objetivo)
    else:
        hablar("Cuentame cual es tu objetivo, por ejemplo: 'Mi objetivo es aumentar masa muscular'.")
