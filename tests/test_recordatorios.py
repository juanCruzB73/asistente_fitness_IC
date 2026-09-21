"""Validación de recordatorios e integración con los comandos."""

from contextlib import redirect_stdout
import io
import unittest
from unittest.mock import patch

from fitness import recordatorios
from fitness.agente import procesar_comando
from main import main


class RecordatoriosTests(unittest.TestCase):
    def setUp(self):
        parche = patch.object(recordatorios, "recordatorios", [])
        parche.start()
        self.addCleanup(parche.stop)
        self.salida = io.StringIO()
        captura = redirect_stdout(self.salida)
        captura.__enter__()
        self.addCleanup(captura.__exit__, None, None, None)

    def test_creacion_y_listado_por_hora(self):
        for hora, mensaje in [("23:59", "Estirar"), (" 00:00 ", " Entrenar ")]:
            self.assertTrue(recordatorios.agregar_recordatorio(hora, mensaje))
        self.salida.truncate(0)
        self.salida.seek(0)
        recordatorios.consultar_recordatorios()
        texto = self.salida.getvalue()
        self.assertLess(texto.index("00:00: Entrenar"), texto.index("23:59: Estirar"))
        self.assertEqual(len(recordatorios.recordatorios), 2)

    def test_datos_invalidos_no_crean_recordatorios(self):
        for hora in ("24:00", "12:60", "-1:30", "9:00", "12:00:00", "", None):
            with self.subTest(hora=hora):
                self.assertFalse(recordatorios.agregar_recordatorio(hora, "Entrenar"))
        for mensaje in ("", "  ", None):
            self.assertFalse(recordatorios.agregar_recordatorio("18:30", mensaje))
        self.assertEqual(recordatorios.recordatorios, [])

    def test_router_preserva_mensaje_y_no_cambia_objetivo(self):
        with patch("fitness.agente.objetivos.establecer_objetivo") as objetivo:
            procesar_comando("Quiero agregar recordatorio 18:30; Ver mi rutina; revisar progreso y objetivo")
            objetivo.assert_not_called()
        self.assertEqual(recordatorios.recordatorios, [{
            "hora": "18:30", "mensaje": "Ver mi rutina; revisar progreso y objetivo",
        }])
        self.assertIn("Recordatorio agregado para las 18:30", self.salida.getvalue())

    def test_cli_lista_vacia_y_recuperacion_tras_error(self):
        entradas = ["recordatorios", "recordatorio", "recordatorio 25:00; Entrenar",
                    "recordatorio 18:30; Entrenar piernas", "ver recordatorios", "salir"]
        with patch("main.db.inicializar"), patch("builtins.input", side_effect=entradas):
            main()
        texto = self.salida.getvalue()
        self.assertIn("Todavía no tienes recordatorios", texto)
        self.assertIn("Usa: recordatorio HH:MM; mensaje", texto)
        self.assertIn("Indica una hora válida", texto)
        self.assertIn("18:30: Entrenar piernas", texto)
        self.assertIn("Hasta la proxima", texto)
        self.assertEqual(len(recordatorios.recordatorios), 1)


if __name__ == "__main__":
    unittest.main()
