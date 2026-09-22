"""Entrada/salida intercambiable: texto o micrófono con transcripción en Google."""

import re
import locale
import sys
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


def _crear_motor():
    """En Windows usa SAPI síncrono para evitar pérdidas entre respuestas."""
    if sys.platform == 'win32':
        from win32com.client import Dispatch
        motor = Dispatch('SAPI.SpVoice')
        for voz in motor.GetVoices():
            idiomas = voz.GetAttribute('Language').split(';')
            if any(locale.windows_locale.get(int(codigo, 16), '').startswith('es')
                   for codigo in idiomas if codigo):
                motor.Voice = voz
                break
        return motor
    import pyttsx3
    motor = pyttsx3.init()
    for voz in motor.getProperty('voices'):
        idiomas = ' '.join(
            idioma.decode('utf-8', errors='ignore') if isinstance(idioma, bytes) else idioma
            for idioma in voz.languages
        ).lower()
        if 'es' in idiomas or 'spanish' in voz.name.lower():
            motor.setProperty('voice', voz.id)
            break
    return motor


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
    print('Modo voz:Requiere Internet.')
    try:
        import speech_recognition as sr
        reconocedor = sr.Recognizer()
        reconocedor.operation_timeout = 10
        with sr.Microphone() as fuente:
            print('Calibrando micrófono; mantené silencio un momento.')
            reconocedor.adjust_for_ambient_noise(fuente, duration=0.5)
        motor = _motor or _crear_motor()
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
            if sys.platform == 'win32':
                # SVSFIsNotXML: lee texto literal y espera a terminar (sin async).
                _motor.Speak(str(mensaje), 16)
            else:
                _motor.say(str(mensaje))
                _motor.runAndWait()
        except Exception as error:
            _modo = 'texto'
            print(f'Falló la salida de voz: {error}. Continuamos en modo texto.')


def escuchar(prompt='Tu: '):
    """Adapta registros dictados y ofrece captura guiada si faltan separadores."""
    texto = _escuchar_entrada(prompt)
    if _modo != 'voz':
        return texto
    registro = re.fullmatch(r'(?:quiero\s+)?registrar\b\s*(.*)', texto, re.IGNORECASE)
    if not registro or ';' in registro[1]:
        return texto
    numero = r'\d+(?:[.,]\d+)?'
    datos = re.fullmatch(
        rf'([^\d;]+?)\s+(?:con\s+)?({numero})\s*(?:kilos?|kilogramos?|kg)'
        r'\s*,?\s*(\d+)\s+repeticiones\s*,?\s*(?:y\s+)?(\d+)\s+series',
        registro[1], re.IGNORECASE,
    )
    if datos is None:
        datos = re.fullmatch(
            rf'([^\d;]+?)\s+({numero})\s+(\d+)[\s:]+(\d+)', registro[1]
        )
    if datos:
        return 'registrar ' + '; '.join(dato.strip() for dato in datos.groups())

    hablar('Vamos a registrar los datos por separado. Podés decir cancelar en cualquier paso.')
    valores = []
    preguntas = ('¿Qué ejercicio hiciste?', '¿Cuántos kilos usaste? Decí solo el número.',
                 '¿Cuántas repeticiones hiciste? Decí solo el número.',
                 '¿Cuántas series hiciste? Decí solo el número.')
    for pregunta in preguntas:
        hablar(pregunta)
        respuesta = _escuchar_entrada().strip()
        if respuesta.lower() in ('salir', 'chau', 'exit', 'modo texto'):
            return respuesta
        if not respuesta or respuesta.lower() == 'cancelar' or _modo != 'voz':
            hablar('Registro cancelado. No se guardaron datos.')
            return ''
        if ';' in respuesta:
            hablar('Registro cancelado: decí un solo dato por respuesta.')
            return ''
        valores.append(respuesta)
    hablar(f'Entendí: {valores[0]}, {valores[1]} kilos, {valores[2]} repeticiones '
           f'y {valores[3]} series. ¿Confirmás? Decí sí o no.')
    confirmacion = _escuchar_entrada().strip().lower()
    if confirmacion in ('salir', 'chau', 'exit', 'modo texto'):
        return confirmacion
    if _modo == 'voz' and confirmacion in ('sí', 'si', 'confirmar', 'confirmo'):
        return 'registrar ' + '; '.join(valores)
    hablar('Registro cancelado. No se guardaron datos.')
    return ''


def _escuchar_entrada(prompt='Tu: '):
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
