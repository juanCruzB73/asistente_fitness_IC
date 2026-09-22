"""Bloque 9 - Bucle CLI del Agente Virtual de Fitness."""

from fitness import db
from fitness.agente import procesar_comando
from fitness.voz import configurar_modo, escuchar, hablar

MENU = """
Comandos que entiendo por ahora:
  - Fijar objetivo:     "Quiero aumentar masa muscular"
                        O bien: "Mi objetivo es ganar fuerza"
  - Consultar objetivo: "Cual es mi objetivo?"
  - Consultar rutina:   "Quiero ver mi rutina de piernas"
                        Grupos: pecho, espalda, piernas
                        También puedes escribir solo el grupo: "piernas"
  - Registrar ejercicio: "registrar sentadillas; 40; 10; 3"
                         Orden: ejercicio; peso en kg; repeticiones; series
                         Usa 0 kg si no hay carga y punto o coma para decimales.
  - Consultar historial: "historial de sentadillas"
                         Muestra el último entrenamiento del ejercicio.
  - Analizar progreso:  "progreso de sentadillas"
                        Compara el primer y el último peso registrado.
  - ayuda:              muestra esta ayuda
  - Crear recordatorio: "recordatorio 18:30; Entrenar piernas"
  - Ver recordatorios:  "recordatorios"
  - salir:              termina el programa (también Ctrl+C o Ctrl+D)
  - modo voz:           activa micrófono y respuesta hablada
  - modo texto:         vuelve al teclado
"""


def main(modo="texto"):
    """Inicializa la base y ejecuta la sesión hasta salir o cerrar la entrada."""
    db.inicializar()

    try:
        configurar_modo(modo)
        hablar("Bienvenido a tu agente de fitness.")
        hablar(MENU)
        _ejecutar_bucle()
    except (EOFError, KeyboardInterrupt):
        # Deja la despedida en otra línea si había un prompt activo.
        print()
    hablar("Hasta la proxima. A entrenar!")


def _ejecutar_bucle():
    """Procesa entradas y comandos de control sin reenviarlos al router."""
    while True:
        entrada = escuchar().strip()

        if not entrada:
            continue

        comando = entrada.lower()

        if comando in ("salir", "chau", "exit"):
            return

        if comando in ("ayuda", "help"):
            hablar(MENU)
            continue

        if comando in ("modo texto", "modo voz"):
            modo = comando.split()[1]
            if configurar_modo(modo):
                hablar(f"Modo {modo} activado.")
            continue

        procesar_comando(entrada)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Asistente personal de fitness")
    parser.add_argument("--interfaz", choices=("terminal", "grafica"), default="terminal",
                        help="Abre la terminal o la ventana de Tkinter.")
    parser.add_argument("--modo", choices=("texto", "voz"), default="texto",
                        help="Voz envía audio a Google y requiere dependencias opcionales.")
    opciones = parser.parse_args()
    if opciones.interfaz == "grafica":
        if opciones.modo == "voz":
            parser.error("El modo voz está disponible en la interfaz terminal.")
        try:
            from fitness.gui import iniciar
        except ImportError as error:
            parser.exit(1, f"No se pudo cargar Tkinter: {error}. Consultá README.md.\n")
        raise SystemExit(iniciar())
    main(opciones.modo)
