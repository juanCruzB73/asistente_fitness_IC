# Asistente virtual de fitness

Aplicación de terminal para guardar objetivos, consultar rutinas, registrar
entrenamientos y comparar el peso utilizado en un ejercicio. Funciona por texto;
la integración con voz corresponde a una etapa posterior.

## Ejecutar

Requiere Python 3 con SQLite y utiliza únicamente la biblioteca estándar.
Desde la raíz del proyecto:

```bash
python3 main.py
```

La primera ejecución crea `fitness.db` en el directorio desde el que se ejecuta
el comando. No requiere instalar dependencias ni servicios externos.

## Comandos

| Acción | Ejemplo |
| --- | --- |
| Fijar objetivo | `Mi objetivo es ganar fuerza` |
| Fijar objetivo con frase breve | `Quiero aumentar masa muscular` |
| Consultar objetivo | `Quiero ver mi objetivo` |
| Consultar rutina | `Quiero ver mi rutina de piernas` |
| Consultar por grupo | `piernas` (también `pecho` y `espalda`) |
| Registrar entrenamiento | `registrar Sentadillas; 40; 10; 3` |
| Consultar último entrenamiento | `historial de Sentadillas` |
| Comparar primer y último peso | `progreso de Sentadillas` |
| Crear recordatorio | `recordatorio 18:30; Entrenar piernas` |
| Listar recordatorios | `recordatorios` |
| Mostrar ayuda | `ayuda` o `help` |
| Terminar | `salir`, `chau`, `exit`, Ctrl+C o fin de entrada (Ctrl+D) |

El registro recibe **ejercicio; peso en kg; repeticiones; series**. El peso puede
ser cero y admite punto o coma decimal. Las repeticiones y series deben ser
enteros positivos. Los nombres de ejercicios se consultan sin distinguir
mayúsculas, incluidas letras acentuadas; las tildes sí forman parte del nombre.

El router reconoce formatos definidos, no lenguaje natural arbitrario. Para
un objetivo libre, usá `Mi objetivo es ...`. Una entrada vacía se ignora y los
comandos desconocidos muestran orientación sin terminar la sesión.

## Datos y límites actuales

- SQLite conserva objetivos y entrenamientos entre sesiones. El objetivo actual
  es el último insertado. Cada entrenamiento guarda la fecha y hora local.
- El historial devuelve el último registro por fecha. El progreso compara el
  primer y el último peso y requiere dos registros; los empates de fecha se
  resuelven por id. No analiza series, repeticiones ni volumen de entrenamiento.
- Las rutinas son listas fijas en `fitness/rutinas.py`.
- Los recordatorios viven en memoria durante el proceso: se pierden al cerrar y
  no generan avisos automáticos.
- Los errores de almacenamiento se propagan; la CLI todavía no ofrece un flujo
  de recuperación para una base inaccesible o dañada.

## Pruebas y ejemplo

```bash
python3 -m unittest discover -s tests -v
```

Las pruebas usan bases temporales o dobles de prueba. Incluyen ejecución real
del CLI, persistencia entre sesiones, validaciones y cierre por teclado.
El [ejemplo de interacción](ejemplos/README.md) explica cómo reproducir el flujo
completo y sus resultados. Ejecutarlo manualmente agrega registros a la base;
la prueba automatizada del ejemplo utiliza un directorio temporal.

## Organización del código

| Archivo | Responsabilidad |
| --- | --- |
| `main.py` | Inicialización, ayuda, lectura en bucle y cierre |
| `fitness/voz.py` | `escuchar()` y `hablar()` como entrada y salida de texto |
| `fitness/agente.py` | Reconocer comandos y delegar a las funciones de dominio |
| `fitness/objetivos.py` | Guardar y consultar objetivos |
| `fitness/rutinas.py` | Catálogo y presentación de rutinas |
| `fitness/entrenamientos.py` | Validar, guardar y consultar entrenamientos |
| `fitness/progreso.py` | Comparar pesos del mismo ejercicio |
| `fitness/recordatorios.py` | Validar y listar recordatorios de la sesión |
| `fitness/db.py` | Abrir conexiones y crear tablas |
| `tests/` | Pruebas unitarias e integración |

El flujo es `main → escuchar → procesar_comando → función de dominio → hablar`.
Las funciones persistentes acceden a SQLite mediante `db.conectar()`. `main()`
llama una vez a `db.inicializar()` antes de recibir comandos.

## Ampliar el asistente

1. Implementá la nueva operación en el módulo de dominio correspondiente, con
   su validación y docstring. Los módulos de dominio no deben importar el router
   ni el bucle principal.
2. Agregá una intención al router que extraiga los argumentos y llame a esa
   función. Priorizá formatos explícitos antes de frases generales y no busques
   palabras clave dentro de los datos de un registro o recordatorio.
3. Actualizá `MENU` en `main.py`, esta guía y las pruebas del comportamiento.
   El bucle de lectura no necesita cambios para un comando de dominio nuevo.
4. Si necesitás persistencia nueva, ampliá el esquema en `db.inicializar()`;
   `CREATE TABLE IF NOT EXISTS` no migra columnas de tablas existentes.

Para agregar un grupo muscular basta ampliar el diccionario `rutinas`: el router
lee sus claves. Actualizá también los grupos anunciados en la ayuda.

Las consultas comunican su resultado mediante `hablar()` y devuelven `None`.
`registrar_ejercicio()` y `agregar_recordatorio()` devuelven `True` al guardar y
`False` ante datos inválidos. Las conexiones devueltas por `db.conectar()` deben
cerrarse; el contexto de transacción de SQLite no cierra la conexión por sí solo.
Al invocar funciones persistentes fuera del CLI, inicializá antes la base.

Para la futura voz, el punto de extensión es `fitness/voz.py`. Las operaciones de
dominio ya usan `hablar()`; la ayuda y el salto de línea al interrumpir todavía
usan `print()` en `main.py`. Esa salida debe revisarse al integrar el modo de voz.

El avance y las etapas pendientes están en [PLAN_DE_TRABAJO.md](PLAN_DE_TRABAJO.md).
