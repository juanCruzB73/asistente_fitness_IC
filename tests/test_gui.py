"""Pruebas de widgets reales; requieren Tkinter y una pantalla disponible."""

from contextlib import closing, redirect_stdout
import io
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from fitness import db, recordatorios
from fitness.voz import hablar, usar_salida

try:
    import tkinter as tk
    from fitness.gui import AplicacionFitness
except ImportError:
    tk = None


class SalidaTests(unittest.TestCase):
    def test_restaura_salida_incluso_tras_excepcion(self):
        mensajes = []
        with self.assertRaises(ValueError):
            with usar_salida(mensajes.append):
                hablar('En la ventana')
                raise ValueError('prueba')
        salida = io.StringIO()
        with redirect_stdout(salida):
            hablar('En terminal')
        self.assertEqual(mensajes, ['En la ventana'])
        self.assertIn('Agente: En terminal', salida.getvalue())


@unittest.skipIf(tk is None, 'Tkinter no está instalado')
class GuiTests(unittest.TestCase):
    def setUp(self):
        try:
            self.raiz = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f'Pantalla no disponible: {error}')
        self.addCleanup(self.raiz.destroy)
        self.raiz.withdraw()
        carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(carpeta.cleanup)
        for parche in (patch.object(db, 'NOMBRE_DB', str(Path(carpeta.name) / 'fitness.db')),
                       patch.object(recordatorios, 'recordatorios', [])):
            parche.start()
            self.addCleanup(parche.stop)
        db.inicializar()
        self.app = AplicacionFitness(self.raiz)
        self.raiz.update_idletasks()

    def campo(self, nombre, valor):
        entrada = self.app.campos[nombre]
        entrada.delete(0, 'end')
        entrada.insert(0, valor)

    def texto(self):
        return self.app.respuestas.get('1.0', 'end')

    def test_flujo_por_botones(self):
        self.campo('objetivo', 'Ganar fuerza')
        self.app.botones['Guardar objetivo'].invoke()
        self.app.botones['Consultar objetivo'].invoke()
        self.app.grupo.set('piernas')
        self.app.botones['Ver rutina'].invoke()
        self.campo('ejercicio', 'Sentadillas')
        for peso in ('40', '45'):
            self.campo('peso', peso)
            self.app.botones['Guardar entrenamiento'].invoke()
        self.app.botones['Ver último entrenamiento'].invoke()
        self.app.botones['Analizar progreso'].invoke()
        self.campo('mensaje', 'Entrenar')
        self.app.botones['Agregar recordatorio'].invoke()
        self.app.botones['Ver recordatorios'].invoke()
        for esperado in ('Tu objetivo actual es: Ganar fuerza', 'Rutina de piernas',
                         'Último entrenamiento de Sentadillas: 45 kg',
                         'El peso aumentó 5', '18:30: Entrenar'):
            self.assertIn(esperado, self.texto())
        with closing(db.conectar()) as conexion:
            self.assertEqual(conexion.execute('SELECT COUNT(*) FROM entrenamientos').fetchone()[0], 2)

    def test_validacion_y_recuperacion_de_error(self):
        self.app.botones['Guardar objetivo'].invoke()
        self.campo('ejercicio', 'Remo')
        self.campo('peso', '-1')
        self.app.botones['Guardar entrenamiento'].invoke()
        self.campo('hora', '25:00')
        self.campo('mensaje', 'Entrenar')
        self.app.botones['Agregar recordatorio'].invoke()
        with patch('fitness.gui.objetivos.consultar_objetivo',
                   side_effect=sqlite3.OperationalError('solo lectura')) as consulta:
            self.app.ejecutar(consulta)
        self.app.botones['Ver rutina'].invoke()
        for esperado in ('Indica tu objetivo', 'El peso debe ser', 'Indica una hora válida',
                         'No se pudo completar', 'Rutina de pecho'):
            self.assertIn(esperado, self.texto())
        self.assertEqual(recordatorios.recordatorios, [])
        with closing(db.conectar()) as conexion:
            self.assertEqual(conexion.execute('SELECT COUNT(*) FROM objetivos').fetchone()[0], 0)
            self.assertEqual(conexion.execute('SELECT COUNT(*) FROM entrenamientos').fetchone()[0], 0)


if __name__ == '__main__':
    unittest.main()
