"""Adaptador de voz probado con dispositivos y servicios simulados."""

from contextlib import redirect_stdout
import io
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

from fitness import voz
from main import main


class VozTests(unittest.TestCase):
    def setUp(self):
        self.sr = MagicMock()
        self.sr.WaitTimeoutError = type('WaitTimeoutError', (Exception,), {})
        self.sr.UnknownValueError = type('UnknownValueError', (Exception,), {})
        self.motor = MagicMock()
        self.motor.getProperty.return_value = [SimpleNamespace(languages=[b'\x05es'], name='Spanish', id='es')]
        self.tts = MagicMock()
        self.tts.init.return_value = self.motor
        for parche in (
            patch.dict('sys.modules', speech_recognition=self.sr, pyttsx3=self.tts),
            patch.object(voz, '_modo', 'texto'), patch.object(voz, '_motor', None),
            patch.object(voz, '_sr', None), patch.object(voz, '_reconocedor', None),
        ):
            parche.start()
            self.addCleanup(parche.stop)
        captura = redirect_stdout(io.StringIO())
        captura.__enter__()
        self.addCleanup(captura.__exit__, None, None, None)

    def test_texto_no_inicializa_audio(self):
        voz.configurar_modo('texto')
        with patch('builtins.input', return_value='piernas'):
            self.assertEqual(voz.escuchar(), 'piernas')
        voz.hablar('Hola')
        self.tts.init.assert_not_called()
        self.sr.Microphone.assert_not_called()

    def test_reconocimiento_y_sintesis(self):
        self.assertTrue(voz.configurar_modo('voz'))
        reconocedor = self.sr.Recognizer.return_value
        reconocedor.recognize_google.return_value = 'registrar Sentadillas punto y coma 40 punto y coma 10 punto y coma 3.'
        self.assertEqual(voz.escuchar(), 'registrar Sentadillas ; 40 ; 10 ; 3')
        reconocedor.recognize_google.assert_called_once_with(reconocedor.listen.return_value, language='es-AR')
        self.assertEqual(reconocedor.operation_timeout, 10)
        voz.hablar('Registro guardado')
        self.motor.say.assert_called_with('Registro guardado')
        self.motor.runAndWait.assert_called_once()
        self.motor.setProperty.assert_called_with('voice', 'es')

    def test_silencio_audio_incomprensible_y_fallo_de_servicio(self):
        voz.configurar_modo('voz')
        reconocedor = self.sr.Recognizer.return_value
        for error in (self.sr.WaitTimeoutError, self.sr.UnknownValueError):
            reconocedor.listen.side_effect = error
            self.assertEqual(voz.escuchar(), '')
            self.assertEqual(voz._modo, 'voz')
        reconocedor.listen.side_effect = OSError('Sin micrófono')
        self.assertEqual(voz.escuchar(), '')
        self.assertEqual(voz._modo, 'texto')
        reconocedor.listen.side_effect = None
        voz.configurar_modo('voz')
        reconocedor.recognize_google.side_effect = RuntimeError('Sin red')
        self.assertEqual(voz.escuchar(), '')
        self.assertEqual(voz._modo, 'texto')

    def test_fallos_de_dependencias_y_sintesis(self):
        with patch.dict('sys.modules', speech_recognition=None):
            self.assertFalse(voz.configurar_modo('voz'))
        self.assertEqual(voz._modo, 'texto')
        voz.configurar_modo('voz')
        self.motor.runAndWait.side_effect = RuntimeError('Sin altavoz')
        voz.hablar('Hola')
        self.assertEqual(voz._modo, 'texto')

    def test_cli_voz_router_respuesta_y_cambio_a_texto(self):
        self.sr.Recognizer.return_value.recognize_google.side_effect = ['piernas', 'modo texto']
        with patch('main.db.inicializar'), patch('builtins.input', return_value='salir'):
            main(modo='voz')
        mensajes = [llamada.args[0] for llamada in self.motor.say.call_args_list]
        self.assertTrue(any('Rutina de piernas:' in mensaje for mensaje in mensajes))
        self.assertEqual(voz._modo, 'texto')


if __name__ == '__main__':
    unittest.main()
