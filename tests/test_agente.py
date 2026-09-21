"""Pruebas de intención y argumentos del router sin modificar la base de datos."""

from contextlib import ExitStack
import unittest
from unittest.mock import patch

from fitness.agente import procesar_comando


class AgenteTests(unittest.TestCase):
    def setUp(self):
        pila = ExitStack()
        self.addCleanup(pila.close)
        self.acciones = {
            nombre: pila.enter_context(patch('fitness.agente.' + nombre))
            for nombre in (
                'objetivos.establecer_objetivo', 'objetivos.consultar_objetivo',
                'rutinas.mostrar_rutina', 'entrenamientos.registrar_ejercicio',
                'entrenamientos.consultar_historial', 'progreso.analizar_progreso',
                'recordatorios.agregar_recordatorio', 'recordatorios.consultar_recordatorios',
                'hablar',
            )
        }

    def test_consultas_y_objetivos(self):
        casos = [
            ('¿Cuál es mi objetivo?', 'objetivos.consultar_objetivo', ()),
            ('Quiero ver mi objetivo', 'objetivos.consultar_objetivo', ()),
            ('MI OBJETIVO ES mejorar mi rutina', 'objetivos.establecer_objetivo', ('mejorar mi rutina',)),
            ('Mi meta es ganar fuerza', 'objetivos.establecer_objetivo', ('ganar fuerza',)),
            ('Quiero aumentar masa muscular', 'objetivos.establecer_objetivo', ('aumentar masa muscular',)),
            ('Quiero ver mi rutina de piernas', 'rutinas.mostrar_rutina', ('piernas',)),
            ('PIERNAS', 'rutinas.mostrar_rutina', ('piernas',)),
            ('Quiero entrenar espalda', 'rutinas.mostrar_rutina', ('espalda',)),
            ('Consultar historial de Press de banca', 'entrenamientos.consultar_historial', ('Press de banca',)),
            ('Quiero ver mi progreso de JALÓN', 'progreso.analizar_progreso', ('JALÓN',)),
            ('Quiero ver mis recordatorios', 'recordatorios.consultar_recordatorios', ()),
            ('rutina para las piernas', 'rutinas.mostrar_rutina', ('piernas',)),
        ]
        for comando, accion, argumentos in casos:
            with self.subTest(comando=comando):
                for mock in self.acciones.values():
                    mock.reset_mock()
                procesar_comando(comando)
                self.acciones[accion].assert_called_once_with(*argumentos)
                for nombre, mock in self.acciones.items():
                    if nombre != accion:
                        mock.assert_not_called()

    def test_desconocidos_y_vacios_no_mutan_datos(self):
        for comando in ('Quiero pizza', 'metal', 'objetivamente', '', None, 'Mi objetivo es'):
            with self.subTest(comando=comando):
                procesar_comando(comando)
        for nombre, mock in self.acciones.items():
            if nombre != 'hablar':
                mock.assert_not_called()
        self.assertEqual(self.acciones['hablar'].call_count, 6)

    def test_palabras_en_datos_no_cambian_intencion(self):
        procesar_comando('recordatorio 18:30; Ver rutina; revisar progreso!')
        self.acciones['recordatorios.agregar_recordatorio'].assert_called_once_with(
            '18:30', ' Ver rutina; revisar progreso!')
        self.acciones['rutinas.mostrar_rutina'].assert_not_called()
        self.acciones['progreso.analizar_progreso'].assert_not_called()


if __name__ == '__main__':
    unittest.main()
