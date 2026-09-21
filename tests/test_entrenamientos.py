"""Pruebas del registro y su integración con la terminal usando una DB temporal."""

from contextlib import closing, redirect_stdout
from datetime import datetime
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fitness import db
from fitness.entrenamientos import registrar_ejercicio
from main import main


class RegistroTests(unittest.TestCase):
    def setUp(self):
        carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(carpeta.cleanup)
        parche = patch.object(db, "NOMBRE_DB", str(Path(carpeta.name) / "fitness.db"))
        parche.start()
        self.addCleanup(parche.stop)
        db.inicializar()
        self.salida = io.StringIO()
        captura = redirect_stdout(self.salida)
        captura.__enter__()
        self.addCleanup(captura.__exit__, None, None, None)

    def registros(self):
        with closing(db.conectar()) as conexion:
            return conexion.execute(
                "SELECT ejercicio, peso, repeticiones, series, fecha FROM entrenamientos"
            ).fetchall()

    def test_persistencia_fecha_y_confirmacion(self):
        inicio = datetime.now().replace(microsecond=0)
        self.assertTrue(registrar_ejercicio(" Sentadillas ", "40,5", 10, 3))
        fila, = self.registros()
        self.assertEqual(fila[:4], ("Sentadillas", 40.5, 10, 3))
        self.assertLessEqual(inicio, datetime.fromisoformat(fila[4]))
        self.assertLessEqual(datetime.fromisoformat(fila[4]), datetime.now())
        self.assertIn("40.5 kg, 3 series de 10 repeticiones", self.salida.getvalue())

    def test_datos_invalidos_no_se_guardan(self):
        for datos in [
            ("", 10, 10, 3), ("Press", -1, 10, 3),
            ("Press", "nan", 10, 3), ("Press", "inf", 10, 3),
            ("Press", "mucho", 10, 3), ("Press", 10, 0, 3),
            ("Press", 10, 2.5, 3), ("Press", 10, 10, -1),
            ("Press", 10, 10, 2**63), ("Press", True, 10, 3),
        ]:
            with self.subTest(datos=datos):
                self.assertFalse(registrar_ejercicio(*datos))
        self.assertEqual(self.registros(), [])

    def test_cli_se_recupera_y_no_confunde_registro_con_objetivo(self):
        entradas = [
            "registrar", "registrar Press; mal; 10; 3",
            "Quiero registrar Flexiones; 0; 12; 4", "salir",
        ]
        with patch("builtins.input", side_effect=entradas):
            main()
        fila, = self.registros()
        self.assertEqual(fila[:4], ("Flexiones", 0, 12, 4))
        with closing(db.conectar()) as conexion:
            self.assertEqual(conexion.execute("SELECT COUNT(*) FROM objetivos").fetchone()[0], 0)
        self.assertIn("Usa: registrar", self.salida.getvalue())
        self.assertIn("Hasta la proxima", self.salida.getvalue())


if __name__ == "__main__":
    unittest.main()
