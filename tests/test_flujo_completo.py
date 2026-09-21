"""Ejecuta el CLI real con bases temporales y verifica persistencia entre sesiones."""

from contextlib import closing
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

RAIZ = Path(__file__).resolve().parents[1]


class FlujoCompletoTests(unittest.TestCase):
    def ejecutar(self, carpeta, comandos):
        resultado = subprocess.run(
            [sys.executable, str(RAIZ / 'main.py')], cwd=carpeta,
            input=comandos, text=True, encoding='utf-8', capture_output=True, timeout=10,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(resultado.stderr, '')
        self.assertIn('Hasta la proxima', resultado.stdout)
        return resultado.stdout

    def test_ejemplo_y_persistencia_entre_sesiones(self):
        comandos = (RAIZ / 'ejemplos/interaccion.txt').read_text(encoding='utf-8')
        with tempfile.TemporaryDirectory() as carpeta:
            salida = self.ejecutar(carpeta, comandos)
            esperados = [
                'Tu objetivo ha sido registrado: aumentar masa muscular',
                'Tu objetivo actual es: aumentar masa muscular',
                'Rutina de piernas:', '1. Sentadillas',
                'Entrenamiento registrado: Sentadillas, 40 kg',
                'Necesitas al menos dos registros',
                'Entrenamiento registrado: Sentadillas, 45 kg',
                'Último entrenamiento de Sentadillas: 45 kg, 3 series de 10 repeticiones',
                'El peso aumentó 5',
                'Recordatorio agregado para las 18:30: Entrenar piernas',
                '18:30: Entrenar piernas',
            ]
            posicion = 0
            for esperado in esperados:
                indice = salida.find(esperado, posicion)
                self.assertGreaterEqual(indice, 0, esperado)
                posicion = indice + len(esperado)
            segunda = self.ejecutar(carpeta,
                'Cual es mi objetivo?\nhistorial de sentadillas\nprogreso de sentadillas\nrecordatorios\nsalir\n')
            self.assertIn('Tu objetivo actual es: aumentar masa muscular', segunda)
            self.assertIn('Último entrenamiento de Sentadillas: 45 kg', segunda)
            self.assertIn('El peso aumentó 5', segunda)
            self.assertIn('Todavía no tienes recordatorios en esta sesión', segunda)
            with closing(sqlite3.connect(Path(carpeta) / 'fitness.db')) as conexion:
                self.assertEqual(conexion.execute('SELECT peso, repeticiones, series FROM entrenamientos ORDER BY id').fetchall(),
                                 [(40, 10, 3), (45, 10, 3)])
                self.assertEqual(conexion.execute('SELECT COUNT(*) FROM objetivos').fetchone()[0], 1)

    def test_casos_limite_no_guardan_datos_y_permiten_continuar(self):
        comandos = '\n'.join([
            '', 'Cual es mi objetivo?', 'historial de Remo', 'progreso de Remo',
            'rutina de brazos', 'comando desconocido',
            'registrar Remo; -1; 10; 3', 'registrar Remo; 20; 2.5; 3',
            'recordatorio 24:00; Entrenar', 'recordatorios', 'piernas', 'salir', '',
        ])
        with tempfile.TemporaryDirectory() as carpeta:
            salida = self.ejecutar(carpeta, comandos)
            for esperado in [
                'Todavia no tienes un objetivo registrado',
                "Todavía no tienes registros de 'Remo'",
                "No existe una rutina para 'brazos'", 'No entendi el comando',
                'El peso debe ser', 'Las repeticiones y las series deben ser',
                'Indica una hora válida', 'Todavía no tienes recordatorios',
                'Rutina de piernas:',
            ]:
                self.assertIn(esperado, salida)
            with closing(sqlite3.connect(Path(carpeta) / 'fitness.db')) as conexion:
                self.assertEqual(conexion.execute('SELECT COUNT(*) FROM entrenamientos').fetchone()[0], 0)
                self.assertEqual(conexion.execute('SELECT COUNT(*) FROM objetivos').fetchone()[0], 0)


if __name__ == '__main__':
    unittest.main()
