# Plan de Trabajo — Agente Virtual de Fitness

> **Área temática:** Fitness y actividad física.
> **Meta general:** Ampliar el asistente virtual base para convertirlo en un asistente personal de entrenamiento que registra objetivos, gestiona rutinas, guarda progreso y responde al usuario.
> **Enfoque de entrega:** El agente se construye **primero como CLI** (entrada y salida por texto en la terminal). La integración con voz (reconocimiento y respuesta auditiva) queda como una fase posterior, una vez que toda la lógica funciona por texto.

---

## Resumen de bloques

| Estado | # | Bloque | Depende de | Prioridad |
|:---:|---|--------|-----------|-----------|
| [x] | 0 | Preparación y diseño | — | Alta |
| [x] | 1 | Base de datos y persistencia | 0 | Alta |
| [x] | 2 | Gestión de objetivos | 0 | Alta |
| [x] | 3 | Gestión de rutinas | 0 | Alta |
| [ ] | 4 | Registro de entrenamientos | 1 | Alta |
| [ ] | 5 | Consulta de historial | 1, 4 | Alta |
| [ ] | 6 | Análisis de progreso | 1, 4 | Media |
| [ ] | 7 | Recordatorios | 0 | Media |
| [~] | 8 | Comprensión de comandos (router) | 2–7 | Alta |
| [~] | 9 | Bucle CLI (interfaz por texto) | 8 | Alta |
| [ ] | 10 | Pruebas y ejemplo de interacción | 2–9 | Alta |
| [ ] | 11 | Documentación y modularidad | Todos | Media |
| [ ] | 12 | Integración con voz (fase posterior) | 10 | Media |
| [ ] | 13 | Ampliaciones futuras (opcional) | 10 | Baja |

> Leyenda: `[x]` completado · `[~]` parcial (base para testear) · `[ ]` pendiente.

---

## Bloque 0 — Preparación y diseño

**Objetivo:** Dejar lista la estructura del proyecto y decidir las librerías.

**Tareas:**
- Definir la estructura modular de archivos (voz, agente, objetivos, rutinas, entrenamientos, progreso, recordatorios, base de datos).
- Investigar y confirmar librerías: `datetime`, `sqlite3`, `statistics`, `tkinter` (opcional).
- Crear el esqueleto de funciones vacías (`establecer_objetivo`, `mostrar_rutina`, `registrar_ejercicio`, etc.).
- Definir `hablar(mensaje)` como salida (en esta etapa: `print` a la terminal) y `escuchar()` como entrada (en esta etapa: `input()`). Así, al pasar a voz solo se cambia el cuerpo de esas dos funciones.

**Hecho cuando:** existe la estructura de módulos, `hablar()`/`escuchar()` funcionan por texto y las librerías están validadas con un pequeño ejemplo de cada una.

---

## Bloque 1 — Base de datos y persistencia

**Objetivo:** Crear el almacenamiento con SQLite.

**Tareas:**
- Crear conexión a `fitness.db`.
- Crear tabla `entrenamientos` (`id`, `ejercicio`, `peso`, `repeticiones`, `series`, `fecha`).
- Encapsular la conexión en una función reutilizable para no repetir código.
- Verificar la creación de la tabla con `CREATE TABLE IF NOT EXISTS`.

**Hecho cuando:** la base de datos se crea automáticamente y se puede insertar/leer un registro de prueba.

---

## Bloque 2 — Gestión de objetivos

**Objetivo:** Permitir registrar y consultar el objetivo del usuario.

**Tareas:**
- Implementar `establecer_objetivo(objetivo)`.
- Implementar `consultar_objetivo()`.
- Mantener el objetivo en estado (variable global o, mejor, persistido en DB para futuras sesiones).

**Hecho cuando:** el usuario puede fijar "Aumentar masa muscular" y el agente lo recuerda al consultarlo.

---

## Bloque 3 — Gestión de rutinas

**Objetivo:** Almacenar y mostrar rutinas por grupo muscular.

**Tareas:**
- Definir el diccionario `rutinas` (pecho, espalda, piernas...).
- Implementar `mostrar_rutina(grupo_muscular)` con manejo del caso "no existe".
- Formatear la respuesta como lista legible.

**Hecho cuando:** `mostrar_rutina("piernas")` responde con los ejercicios correctos.

---

## Bloque 4 — Registro de entrenamientos

**Objetivo:** Guardar cada ejercicio realizado en la base de datos.

**Tareas:**
- Implementar `registrar_ejercicio(ejercicio, peso, repeticiones, series)`.
- Sellar cada registro con fecha (`datetime.now()`).
- Confirmar por voz/texto el registro guardado.

**Hecho cuando:** un ejercicio se inserta correctamente y el agente confirma los datos.

---

## Bloque 5 — Consulta de historial

**Objetivo:** Responder qué hizo el usuario la última vez en un ejercicio.

**Tareas:**
- Implementar `consultar_historial(ejercicio)`.
- Ordenar por fecha descendente y devolver el último registro.
- Manejar el caso sin registros.

**Hecho cuando:** el agente responde el último peso/series/reps de un ejercicio dado.

---

## Bloque 6 — Análisis de progreso

**Objetivo:** Comparar el primer y el último registro de un ejercicio.

**Tareas:**
- Implementar `analizar_progreso(ejercicio)`.
- Calcular la diferencia de peso (aumento, disminución o igual).
- (Opcional) usar `statistics` para promedios.
- Manejar el caso con menos de dos registros.

**Hecho cuando:** el agente informa la evolución de peso desde el primer registro.

---

## Bloque 7 — Recordatorios

**Objetivo:** Gestionar avisos de entrenamiento.

**Tareas:**
- Implementar `agregar_recordatorio(hora, mensaje)`.
- Mantener la lista de recordatorios.
- (Opcional) verificar la hora actual para disparar avisos.

**Hecho cuando:** se puede crear un recordatorio y el agente lo confirma.

---

## Bloque 8 — Comprensión de comandos (router)

**Objetivo:** Interpretar la solicitud del usuario y llamar a la función correcta.

**Tareas:**
- Implementar `procesar_comando(comando)`.
- Detectar palabras clave: objetivo, rutina, historial, progreso, grupos musculares.
- Definir respuesta por defecto para comandos no reconocidos.

**Hecho cuando:** frases como "Quiero ver mi rutina de piernas" ejecutan la función correspondiente.

---

## Bloque 9 — Bucle CLI (interfaz por texto)

**Objetivo:** Poner en marcha el agente como aplicación de línea de comandos.

**Tareas:**
- Implementar el bucle principal: leer con `input()`, pasar a `procesar_comando`, imprimir la respuesta.
- Definir comandos de control (`ayuda`, `salir`).
- Mostrar un menú/ayuda inicial con lo que el agente entiende.
- Manejar entrada vacía o inválida sin cortar la ejecución.

**Hecho cuando:** el agente corre en la terminal (`python main.py`), acepta comandos por texto y se cierra limpiamente con `salir`.

---

## Bloque 10 — Pruebas y ejemplo de interacción

**Objetivo:** Validar el flujo completo.

**Tareas:**
- Ejecutar el diálogo de ejemplo (objetivo → rutina → registro → progreso).
- Probar casos límite (sin registros, comando desconocido, grupo inexistente).
- Corregir errores detectados.

**Hecho cuando:** el ejemplo de interacción completa se reproduce sin fallos.

---

## Bloque 11 — Documentación y modularidad

**Objetivo:** Dejar el código mantenible y documentado.

**Tareas:**
- Confirmar que cada funcionalidad es una función independiente.
- Documentar cada función (docstrings) y el flujo general.
- Verificar que agregar una funcionalidad no obliga a reescribir el resto.

**Hecho cuando:** el proyecto está documentado y las funciones son intercambiables.

---

## Bloque 12 — Integración con voz (fase posterior)

**Objetivo:** Sumar reconocimiento de voz y respuesta auditiva sobre la lógica ya probada por CLI.

**Tareas:**
- Reemplazar el cuerpo de `escuchar()` por reconocimiento de voz (voz → texto).
- Reemplazar el cuerpo de `hablar()` por síntesis de voz (texto → audio).
- Mantener intacto el resto del código: solo cambian esas dos funciones.
- Permitir alternar entre modo texto y modo voz.

**Hecho cuando:** el agente funciona por voz de extremo a extremo reutilizando toda la lógica del CLI.

---

## Bloque 13 — Ampliaciones futuras (opcional)

**Objetivo:** Dejar propuestas de mejora.

**Ideas:**
- Interfaz gráfica con `tkinter`.
- Gráficos de progreso.
- Cálculo de volumen de entrenamiento (series × reps × peso).
- Perfiles de múltiples usuarios.
- Conexión con dispositivos o apps de actividad física.

**Hecho cuando:** las mejoras quedan listadas como backlog priorizado.

---

## Diagrama de arquitectura

```text
Agente Fitness
│
├── Interfaz / Voz        → Escuchar usuario · Hablar
├── Agente                → Interpretar solicitud (procesar_comando)
├── Objetivos             → Establecer · Consultar
├── Rutinas               → Consultar · Gestionar ejercicios
├── Entrenamientos        → Registrar · Consultar historial
├── Progreso              → Analizar evolución
├── Recordatorios         → Gestionar horarios
└── Base de datos         → SQLite
```
