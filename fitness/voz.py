"""Entrada y salida del agente.
es la comunicacion con el usuario
"""

def hablar(mensaje):
    print(f"Agente: {mensaje}")


def escuchar(prompt="Tu: "):
    return input(prompt)
