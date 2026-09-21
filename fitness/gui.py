"""Interfaz Tkinter que reutiliza las operaciones de dominio y SQLite."""

import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from fitness import db, entrenamientos, objetivos, progreso, recordatorios, rutinas
from fitness.voz import usar_salida


class AplicacionFitness:
    """Formularios de escritorio y panel de respuestas de la sesión."""

    def __init__(self, raiz):
        """Construye la ventana; la base debe estar inicializada previamente."""
        self.raiz = raiz
        raiz.title('Mi entrenamiento · Asistente Fitness')
        raiz.geometry('900x720')
        raiz.minsize(700, 600)
        raiz.columnconfigure(0, weight=1)
        raiz.rowconfigure(0, weight=1)
        estilo = ttk.Style(raiz)
        estilo.configure('Titulo.TLabel', font=('Segoe UI', 22, 'bold'))
        estilo.configure('Subtitulo.TLabel', font=('Segoe UI', 11))
        estilo.configure('TButton', padding=(12, 7))
        estilo.configure('TNotebook.Tab', padding=(12, 8))

        marco = ttk.Frame(raiz, padding=24)
        marco.grid(sticky='nsew')
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(4, weight=1)
        ttk.Label(marco, text='Mi entrenamiento', style='Titulo.TLabel').grid(sticky='w')
        ttk.Label(marco, text='Organizá tus rutinas y seguí tu progreso.',
                  style='Subtitulo.TLabel').grid(sticky='w', pady=(4, 18))
        self.pestanas = ttk.Notebook(marco)
        self.pestanas.grid(row=2, column=0, sticky='ew')
        self.campos = {}
        self.botones = {}
        self._crear_objetivos()
        self._crear_entrenamientos()
        self._crear_consultas()
        self._crear_recordatorios()
        ttk.Label(marco, text='Respuestas del asistente', style='Subtitulo.TLabel').grid(
            row=3, sticky='w', pady=(18, 8))
        self.respuestas = ScrolledText(marco, height=10, wrap='word', state='disabled',
                                      font=('Segoe UI', 11), padx=12, pady=12)
        self.respuestas.grid(row=4, sticky='nsew')
        pie = ttk.Frame(marco)
        pie.grid(row=5, sticky='ew', pady=(10, 0))
        pie.columnconfigure(0, weight=1)
        ttk.Label(pie, text='Objetivos y entrenamientos se guardan automáticamente.').grid(sticky='w')
        ttk.Button(pie, text='Cerrar', command=raiz.destroy).grid(row=0, column=1)
        raiz.protocol('WM_DELETE_WINDOW', raiz.destroy)
        self.mostrar('Bienvenido. Elegí una pestaña para comenzar.')
        self.ejecutar(objetivos.consultar_objetivo)
        self.campos['objetivo'].focus_set()

    def _pestana(self, titulo):
        """Crea un panel con distribución adaptable al ancho de la ventana."""
        panel = ttk.Frame(self.pestanas, padding=16)
        panel.columnconfigure(1, weight=1)
        self.pestanas.add(panel, text=titulo)
        return panel

    def _campo(self, panel, fila, clave, etiqueta, valor=''):
        """Añade un campo etiquetado y conserva su referencia para leerlo."""
        ttk.Label(panel, text=etiqueta).grid(row=fila, column=0, sticky='w', padx=(0, 16), pady=5)
        entrada = ttk.Entry(panel)
        entrada.insert(0, valor)
        entrada.grid(row=fila, column=1, sticky='ew', pady=5)
        self.campos[clave] = entrada
        return entrada

    def _boton(self, panel, fila, titulo, accion):
        """Conecta un botón con una acción protegida contra errores de SQLite."""
        boton = ttk.Button(panel, text=titulo, command=lambda: self.ejecutar(accion))
        boton.grid(row=fila, column=1, sticky='w', pady=5)
        self.botones[titulo] = boton

    def _crear_objetivos(self):
        """Construye los controles para el objetivo y las rutinas disponibles."""
        panel = self._pestana('Objetivo y rutinas')
        self._campo(panel, 0, 'objetivo', 'Tu objetivo')
        self._boton(panel, 1, 'Guardar objetivo', self.guardar_objetivo)
        self._boton(panel, 2, 'Consultar objetivo', objetivos.consultar_objetivo)
        ttk.Label(panel, text='Grupo muscular').grid(row=3, column=0, sticky='w')
        self.grupo = ttk.Combobox(panel, values=list(rutinas.rutinas), state='readonly')
        self.grupo.current(0)
        self.grupo.grid(row=3, column=1, sticky='ew', pady=5)
        self._boton(panel, 4, 'Ver rutina', lambda: rutinas.mostrar_rutina(self.grupo.get()))

    def _crear_entrenamientos(self):
        """Construye el registro con unidades y valores iniciales explícitos."""
        panel = self._pestana('Entrenamiento')
        for fila, (clave, etiqueta, valor) in enumerate([
            ('ejercicio', 'Ejercicio', ''), ('peso', 'Peso (kg)', '0'),
            ('repeticiones', 'Repeticiones', '10'), ('series', 'Series', '3'),
        ]):
            self._campo(panel, fila, clave, etiqueta, valor)
        self._boton(panel, 4, 'Guardar entrenamiento', self.guardar_entrenamiento)
        ttk.Label(panel, text='Peso sin carga: 0 kg. Decimales con punto o coma.').grid(
            row=5, column=0, columnspan=2, sticky='w', pady=5)

    def _crear_consultas(self):
        """Ofrece consultas por ejercicio con las mismas reglas que la terminal."""
        panel = self._pestana('Historial y progreso')
        self._campo(panel, 0, 'consulta', 'Ejercicio')
        self._boton(panel, 1, 'Ver último entrenamiento',
                    lambda: entrenamientos.consultar_historial(self.campos['consulta'].get()))
        self._boton(panel, 2, 'Analizar progreso',
                    lambda: progreso.analizar_progreso(self.campos['consulta'].get()))
        ttk.Label(panel, text='El progreso compara el primer y el último peso registrado.').grid(
            row=3, column=0, columnspan=2, sticky='w', pady=10)

    def _crear_recordatorios(self):
        """Construye controles para la lista temporal de recordatorios."""
        panel = self._pestana('Recordatorios')
        self._campo(panel, 0, 'hora', 'Hora (HH:MM)', '18:30')
        self._campo(panel, 1, 'mensaje', 'Mensaje')
        self._boton(panel, 2, 'Agregar recordatorio', lambda: recordatorios.agregar_recordatorio(
            self.campos['hora'].get(), self.campos['mensaje'].get()))
        self._boton(panel, 3, 'Ver recordatorios', recordatorios.consultar_recordatorios)
        ttk.Label(panel, text='Solo durante esta sesión. No se emiten avisos automáticos.').grid(
            row=4, column=0, columnspan=2, sticky='w', pady=10)

    def guardar_objetivo(self):
        """Valida el campo antes de llamar al almacenamiento de objetivos."""
        objetivo = self.campos['objetivo'].get().strip()
        if not objetivo:
            self.mostrar('Indica tu objetivo antes de guardarlo.')
            self.campos['objetivo'].focus_set()
            return
        objetivos.establecer_objetivo(objetivo)

    def guardar_entrenamiento(self):
        """Guarda los datos del formulario y prepara el nombre para consultas."""
        datos = [self.campos[clave].get() for clave in ('ejercicio', 'peso', 'repeticiones', 'series')]
        if entrenamientos.registrar_ejercicio(*datos):
            self.campos['consulta'].delete(0, 'end')
            self.campos['consulta'].insert(0, datos[0].strip())

    def ejecutar(self, accion):
        """Redirige la respuesta a la ventana y mantiene abierta la app ante errores de DB."""
        with usar_salida(self.mostrar):
            try:
                accion()
            except sqlite3.Error as error:
                self.mostrar(f'No se pudo completar la operación en la base de datos: {error}')

    def mostrar(self, mensaje):
        """Agrega una respuesta al panel de solo lectura y desplaza al final."""
        self.respuestas.configure(state='normal')
        self.respuestas.insert('end', mensaje + '\n\n')
        self.respuestas.configure(state='disabled')
        self.respuestas.see('end')


def iniciar():
    """Inicializa SQLite y ejecuta Tkinter; devuelve un código de salida."""
    raiz = None
    try:
        db.inicializar()
        raiz = tk.Tk()
        AplicacionFitness(raiz)
        raiz.mainloop()
        return 0
    except (tk.TclError, sqlite3.Error) as error:
        print(f'No se pudo iniciar la interfaz gráfica: {error}. Consultá README.md.')
        return 1
    finally:
        if raiz is not None:
            try:
                raiz.destroy()
            except tk.TclError:
                pass
