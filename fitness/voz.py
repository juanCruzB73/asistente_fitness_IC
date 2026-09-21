"""Entrada/salida intercambiable: texto o micrófono con transcripción en Google."""

import re
from contextlib import contextmanager
from contextvars import ContextVar

_salida = ContextVar('salida', default=None)


@contextmanager
def usar_salida(receptor):
    """Deriva respuestas al receptor durante una acción y restaura la salida."""
    token = _salida.set(receptor)
    try:
        yield
    finally:
        _salida.reset(token)

_modo = 'texto'
_sr = None
_reconocedor = None
_motor = None


def configurar_modo(modo):
    """Activa texto o voz; carga dependencias opcionales al activar voz.

    Devuelve False y vuelve a texto si no se puede iniciar el audio.
    El modo voz envía audio a Google para reconocer español de Argentina.
    """
    global _modo, _sr, _reconocedor, _motor
    if modo not in ('texto', 'voz'):
        raise ValueError('El modo debe ser texto o voz.')
    _modo = 'texto'
    if modo == 'texto':
        return True
    print('Modo voz: el audio se enviará a Google para transcribirlo. Requiere Internet.')
    try:
        import speech_recognition as sr
        import pyttsx3
        reconocedor = sr.Recognizer()
        reconocedor.operation_timeout = 10
        with sr.Microphone() as fuente:
            print('Calibrando micrófono; mantené silencio un momento.')
            reconocedor.adjust_for_ambient_noise(fuente, duration=0.5)
        motor = _motor or pyttsx3.init()
        for voz in motor.getProperty('voices'):
            idiomas = ' '.join(
                idioma.decode('utf-8', errors='ignore') if isinstance(idioma, bytes) else idioma
                for idioma in voz.languages
            ).lower()
            if 'es' in idiomas or 'spanish' in voz.name.lower():
                motor.setProperty('voice', voz.id)
                break
        _sr, _reconocedor, _motor = sr, reconocedor, motor
        _modo = 'voz'
        return True
    except Exception as error:
        print(f'No se pudo activar la voz: {error}. Continuamos en modo texto. '
              'Consultá la instalación en README.md.')
        return False


def hablar(mensaje):
    """Muestra el mensaje y, en modo voz, lo sintetiza; vuelve a texto si falla."""
    global _modo
    receptor = _salida.get()
    if receptor is not None:
        receptor(str(mensaje))
        return
    print(f'Agente: {mensaje}')
    if _modo == 'voz':
        try:
            _motor.say(str(mensaje))
            _motor.runAndWait()
        except Exception as error:
            _modo = 'texto'
            print(f'Falló la salida de voz: {error}. Continuamos en modo texto.')


def escuchar(prompt='Tu: '):
    """Lee texto o transcribe una frase; silencio/incomprensión devuelve vacío.

    Limita la espera a 5 segundos y cada frase a 15 segundos. Los fallos de
    servicio o dispositivo vuelven a texto. Ctrl+C y EOF llegan al bucle CLI.
    """
    global _modo
    if _modo == 'texto':
        return input(prompt)
    try:
        with _sr.Microphone() as fuente:
            print('Escuchando… (Ctrl+C para salir)')
            audio = _reconocedor.listen(fuente, timeout=5, phrase_time_limit=15)
        texto = _reconocedor.recognize_google(audio, language='es-AR')
        # Permite dictar el separador de los comandos existentes.
        texto = re.sub(r'\bpunto\s+y\s+coma\b', ';', texto, flags=re.IGNORECASE)
        print(f'Tu (voz): {texto}')
        return texto.strip().rstrip('.?!')
    except _sr.WaitTimeoutError:
        print('No se detectó voz. Intentá de nuevo o usá Ctrl+C para salir.')
        return ''
    except _sr.UnknownValueError:
        hablar('No pude entender el audio. Repetí el comando.')
        return ''
    except Exception as error:
        _modo = 'texto'
        print(f'Falló el reconocimiento: {error}. Continuamos en modo texto.')
        return ''
