"""Bloque 9 - Bucle CLI del Agente Virtual de Fitness."""

from fitness import db
from fitness.agente import procesar_comando
from fitness.voz import escuchar, hablar

MENU = """
Comandos que entiendo por ahora:
  - Fijar objetivo:     "Quiero aumentar masa muscular"
  - Consultar objetivo: "Cual es mi objetivo?"
  - ayuda:              muestra esta ayuda
  - salir:              termina el programa
"""


def main():
    db.inicializar()

    hablar("Bienvenido a tu agente de fitness.")
    print(MENU)

    while True:
        entrada = escuchar().strip()

        if not entrada:
            continue

        comando = entrada.lower()

        if comando in ("salir", "chau", "exit"):
            hablar("Hasta la proxima. A entrenar!")
            break

        if comando in ("ayuda", "help"):
            print(MENU)
            continue

        procesar_comando(entrada)


if __name__ == "__main__":
    main()
