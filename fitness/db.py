"""Conexión SQLite y creación idempotente del esquema de almacenamiento."""

import sqlite3

NOMBRE_DB = "fitness.db"


def conectar():
    """Abre NOMBRE_DB relativo al directorio actual; quien llama debe cerrarla.

    Devuelve sqlite3.Connection. No crea las tablas: llamar antes a inicializar.
    Los errores de SQLite se propagan a quien llama.
    """
    return sqlite3.connect(NOMBRE_DB)


def inicializar():
    """Crea las tablas si no existen. Se llama una vez al iniciar el agente."""
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entrenamientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ejercicio TEXT,
            peso REAL,
            repeticiones INTEGER,
            series INTEGER,
            fecha TEXT
        )
    """)

    # El objetivo se persiste para recordarlo entre sesiones.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS objetivos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            objetivo TEXT,
            fecha TEXT
        )
    """)

    conexion.commit()
    conexion.close()
