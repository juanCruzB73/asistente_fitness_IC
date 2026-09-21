"""Comportamiento de la sesión de terminal y sus formas de cierre."""

from contextlib import redirect_stdout
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from main import MENU, main


class CliTests(unittest.TestCase):
    def test_controles_y_entradas_vacias_no_llegan_al_router(self):
        salida = io.StringIO()
        with patch('main.db.inicializar') as inicializar, \
                patch('main.procesar_comando') as router, \
                patch('builtins.input', side_effect=['', '  ', ' AYUDA ', 'help', 'piernas', ' SALIR ']), \
                redirect_stdout(salida):
            main()
        inicializar.assert_called_once_with()
        router.assert_called_once_with('piernas')
        self.assertEqual(salida.getvalue().count(MENU), 3)
        self.assertEqual(salida.getvalue().count('Hasta la proxima'), 1)

    def test_cierre_por_teclado_o_fin_de_entrada(self):
        for cierre in (EOFError, KeyboardInterrupt):
            with self.subTest(cierre=cierre):
                salida = io.StringIO()
                with patch('main.db.inicializar'), \
                        patch('builtins.input', side_effect=cierre), redirect_stdout(salida):
                    main()
                self.assertEqual(salida.getvalue().count('Hasta la proxima'), 1)

    def test_alias_de_salida(self):
        for comando in ('salir', 'chau', 'exit'):
            with self.subTest(comando=comando), patch('main.db.inicializar'), \
                    patch('builtins.input', return_value=comando), \
                    patch('main.procesar_comando') as router, redirect_stdout(io.StringIO()):
                main()
                router.assert_not_called()

    def test_proceso_real_continua_tras_comandos_invalidos_y_cierra_por_eof(self):
        script = Path(__file__).resolve().parents[1] / 'main.py'
        with tempfile.TemporaryDirectory() as carpeta:
            resultado = subprocess.run(
                [sys.executable, str(script)], cwd=carpeta,
                input='\ncomando desconocido\nregistrar Press; mal; 10; 3\npiernas\nayuda\n',
                text=True, capture_output=True, timeout=10,
            )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(resultado.stderr, '')
        self.assertIn('No entendi el comando', resultado.stdout)
        self.assertIn('El peso debe ser', resultado.stdout)
        self.assertIn('Rutina de piernas', resultado.stdout)
        self.assertIn('Hasta la proxima', resultado.stdout)


if __name__ == '__main__':
    unittest.main()
