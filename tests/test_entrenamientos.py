"""Pruebas del registro y su integración con la terminal usando una DB temporal."""

from contextlib import closing, redirect_stdout
from datetime import datetime
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fitness import db
from fitness.entrenamientos import consultar_historial, registrar_ejercicio
from fitness.progreso import analizar_progreso
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

    def test_historial_ordena_por_fecha_y_desempata_por_id(self):
        with closing(db.conectar()) as conexion:
            with conexion:
                conexion.executemany(
                    "INSERT INTO entrenamientos "
                    "(ejercicio, peso, repeticiones, series, fecha) VALUES (?, ?, ?, ?, ?)",
                    [
                        ("Jalón", 40, 10, 3, "2026-09-20 10:00:00"),
                        ("Jalón", 45, 8, 4, "2026-09-20 10:00:00"),
                        ("Jalón", 20, 12, 2, "2026-09-19 10:00:00"),
                        ("Sentadillas", 60, 6, 5, "2026-09-21 10:00:00"),
                    ],
                )
        consultar_historial(" JALÓN ")
        self.assertIn("Último entrenamiento de Jalón: 45 kg, 4 series de 8 repeticiones", self.salida.getvalue())
        self.assertIn("2026-09-20 10:00:00", self.salida.getvalue())
        self.assertEqual(len(self.registros()), 4)

    def test_historial_sin_registros_y_sin_nombre(self):
        consultar_historial("Press")
        consultar_historial("  ")
        consultar_historial("' OR 1=1 --")
        self.assertIn("Todavía no tienes registros de 'Press'", self.salida.getvalue())
        self.assertIn("Indica el ejercicio", self.salida.getvalue())
        self.assertEqual(self.registros(), [])

    def test_cli_historial_no_modifica_objetivo(self):
        entradas = [
            "Quiero aumentar masa muscular", "registrar Press de banca; 40; 10; 3",
            "Quiero ver mi historial de PRESS DE BANCA", "historial",
            "historial de remo", "Cual es mi objetivo?", "salir",
        ]
        with patch("builtins.input", side_effect=entradas):
            main()
        self.assertIn("Último entrenamiento de Press de banca: 40 kg", self.salida.getvalue())
        self.assertIn("Indica el ejercicio", self.salida.getvalue())
        self.assertIn("Todavía no tienes registros de 'remo'", self.salida.getvalue())
        self.assertIn("Tu objetivo actual es: aumentar masa muscular", self.salida.getvalue())
        with closing(db.conectar()) as conexion:
            self.assertEqual(conexion.execute("SELECT COUNT(*) FROM objetivos").fetchone()[0], 1)

    def test_progreso_aumento_disminucion_e_igualdad(self):
        for ejercicio, inicial, final, esperado in [
            ("Press", 40, 45, "El peso aumentó 5"),
            ("Remo", 30, 25, "El peso disminuyó 5"),
            ("Flexiones", 0, 0, "El peso se mantuvo igual"),
            ("Jalón", 0.1, 0.3, "El peso aumentó 0.2 kg"),
        ]:
            with self.subTest(ejercicio=ejercicio):
                registrar_ejercicio(ejercicio, inicial, 10, 3)
                registrar_ejercicio(ejercicio, final, 10, 3)
                self.salida.truncate(0)
                self.salida.seek(0)
                analizar_progreso(ejercicio.upper())
                self.assertIn(esperado, self.salida.getvalue())

    def test_progreso_ordena_por_fecha_y_id_y_filtra_ejercicio(self):
        with closing(db.conectar()) as conexion:
            with conexion:
                conexion.executemany(
                    "INSERT INTO entrenamientos "
                    "(ejercicio, peso, repeticiones, series, fecha) VALUES (?, ?, 10, 3, ?)",
                    [
                        ("Jalón", 40, "2026-09-20 10:00:00"),
                        ("Jalón", 45, "2026-09-20 10:00:00"),
                        ("Jalón", 20, "2026-09-19 10:00:00"),
                        ("Jalón", 25, "2026-09-19 10:00:00"),
                        ("Remo", 90, "2026-09-21 10:00:00"),
                    ],
                )
        antes = self.registros()
        analizar_progreso(" JALÓN ")
        self.assertIn("Primer registro: 20 kg (2026-09-19 10:00:00)", self.salida.getvalue())
        self.assertIn("Último registro: 45 kg (2026-09-20 10:00:00)", self.salida.getvalue())
        self.assertIn("El peso aumentó 25", self.salida.getvalue())
        self.assertEqual(antes, self.registros())

    def test_cli_progreso_maneja_datos_insuficientes_y_preserva_objetivo(self):
        entradas = [
            "Quiero aumentar masa muscular", "progreso", "progreso de Remo",
            "registrar Remo; 20; 10; 3", "progreso de Remo",
            "registrar Remo; 25; 10; 3", "Quiero ver mi progreso de REMO",
            "Cual es mi objetivo?", "salir",
        ]
        with patch("builtins.input", side_effect=entradas):
            main()
        texto = self.salida.getvalue()
        self.assertIn("Indica el ejercicio", texto)
        self.assertIn("Todavía no tienes registros de 'Remo'", texto)
        self.assertIn("Necesitas al menos dos registros", texto)
        self.assertIn("El peso aumentó 5", texto)
        self.assertIn("Tu objetivo actual es: aumentar masa muscular", texto)
        self.assertIn("Hasta la proxima", texto)
        with closing(db.conectar()) as conexion:
            self.assertEqual(conexion.execute("SELECT COUNT(*) FROM objetivos").fetchone()[0], 1)

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
