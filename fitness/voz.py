"""Adaptador de entrada y salida por texto; punto de extensión para la voz."""

def hablar(mensaje):
    """Imprime el mensaje con el prefijo del agente; devuelve None."""
    print(f"Agente: {mensaje}")


def escuchar(prompt="Tu: "):
    """Lee una línea; propaga EOFError y KeyboardInterrupt al bucle CLI."""
    return input(prompt)
