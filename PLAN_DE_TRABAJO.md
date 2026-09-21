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
| [x] | 4 | Registro de entrenamientos | 1 | Alta |
| [x] | 5 | Consulta de historial | 1, 4 | Alta |
| [x] | 6 | Análisis de progreso | 1, 4 | Media |
| [x] | 7 | Recordatorios | 0 | Media |
| [x] | 8 | Comprensión de comandos (router) | 2–7 | Alta |
| [x] | 9 | Bucle CLI (interfaz por texto) | 8 | Alta |
| [x] | 10 | Pruebas y ejemplo de interacción | 2–9 | Alta |
| [x] | 11 | Documentación y modularidad | Todos | Media |
| [~] | 12 | Integración con voz (fase posterior) | 10 | Media |
| [x] | 13 | Interfaz gráfica y backlog de ampliaciones | 10 | Baja |

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

**Implementado:** `fitness/entrenamientos.py`, integrado al router y a la ayuda CLI.
Comando: `registrar sentadillas; 40; 10; 3` (ejercicio; kg; repeticiones; series).
Admite peso cero y decimales con punto o coma; rechaza datos inválidos antes de guardar.
Verificación: `python3 -m unittest discover -s tests -v` (persistencia, fecha,
confirmación, validaciones y flujo CLI con base temporal).

---

## Bloque 5 — Consulta de historial

**Objetivo:** Responder qué hizo el usuario la última vez en un ejercicio.

**Tareas:**
- Implementar `consultar_historial(ejercicio)`.
- Ordenar por fecha descendente y devolver el último registro.
- Manejar el caso sin registros.

**Hecho cuando:** el agente responde el último peso/series/reps de un ejercicio dado.

**Implementado:** `consultar_historial(ejercicio)` en `fitness/entrenamientos.py`.
Comando: `historial de sentadillas` o `Quiero ver mi historial de sentadillas`.
Consulta por nombre sin distinguir mayúsculas, ordena por fecha descendente y
desempata por id; informa peso, series, repeticiones y fecha. Maneja ejercicio
omitido o sin registros. Verificado con `python3 -m unittest discover -s tests -v`
(6 pruebas de registro e historial con base temporal).

---

## Bloque 6 — Análisis de progreso

**Objetivo:** Comparar el primer y el último registro de un ejercicio.

**Tareas:**
- Implementar `analizar_progreso(ejercicio)`.
- Calcular la diferencia de peso (aumento, disminución o igual).
- (Opcional) usar `statistics` para promedios.
- Manejar el caso con menos de dos registros.

**Hecho cuando:** el agente informa la evolución de peso desde el primer registro.

**Implementado:** `analizar_progreso(ejercicio)` en `fitness/progreso.py`.
Comando: `progreso de sentadillas` o `Quiero ver mi progreso de sentadillas`.
Compara el primer y el último peso por fecha (desempata por id) e informa
aumento, disminución o igualdad junto con ambas fechas. Maneja nombre omitido
y menos de dos registros. Verificado con `python3 -m unittest discover -s tests -v`
(9 pruebas de registro, historial y progreso con base temporal).

---

## Bloque 7 — Recordatorios

**Objetivo:** Gestionar avisos de entrenamiento.

**Tareas:**
- Implementar `agregar_recordatorio(hora, mensaje)`.
- Mantener la lista de recordatorios.
- (Opcional) verificar la hora actual para disparar avisos.

**Hecho cuando:** se puede crear un recordatorio y el agente lo confirma.

**Implementado:** `agregar_recordatorio(hora, mensaje)` y
`consultar_recordatorios()` en `fitness/recordatorios.py`.
Comandos: `recordatorio 18:30; Entrenar piernas` y `recordatorios`.
Valida hora HH:MM y mensaje no vacío, confirma la creación y lista por hora.
La lista se mantiene en memoria durante la sesión: se pierde al cerrar el
programa. Los avisos automáticos opcionales quedan pendientes.
Verificación: `python3 -m unittest discover -s tests -v` (13 pruebas en total).

---

## Bloque 8 — Comprensión de comandos (router)

**Objetivo:** Interpretar la solicitud del usuario y llamar a la función correcta.

**Tareas:**
- Implementar `procesar_comando(comando)`.
- Detectar palabras clave: objetivo, rutina, historial, progreso, grupos musculares.
- Definir respuesta por defecto para comandos no reconocidos.

**Hecho cuando:** frases como "Quiero ver mi rutina de piernas" ejecutan la función correspondiente.

**Implementado:** router por intención al inicio del comando para los módulos 2–7.
Reconoce consultas, objetivos explícitos, grupos musculares solos y frases como
`Quiero entrenar espalda`. `Quiero ver mi objetivo` consulta sin sobrescribirlo.
Para objetivos libres se usa `Mi objetivo es ...`; se conserva `Quiero aumentar
masa muscular` y verbos afines. Entradas vacías o desconocidas reciben orientación.
Verificado con `python3 -m unittest discover -s tests -v` (16 pruebas en total).

---

## Bloque 9 — Bucle CLI (interfaz por texto)

**Objetivo:** Poner en marcha el agente como aplicación de línea de comandos.

**Tareas:**
- Implementar el bucle principal: leer con `input()`, pasar a `procesar_comando`, imprimir la respuesta.
- Definir comandos de control (`ayuda`, `salir`).
- Mostrar un menú/ayuda inicial con lo que el agente entiende.
- Manejar entrada vacía o inválida sin cortar la ejecución.

**Hecho cuando:** el agente corre en la terminal (`python main.py`), acepta comandos por texto y se cierra limpiamente con `salir`.

**Implementado:** ejecutar `python3 main.py`. La ayuda inicial y `ayuda`/`help`
muestran los comandos disponibles. El bucle ignora entradas vacías y continúa
tras comandos desconocidos o datos inválidos. `salir`, `chau`, `exit`, Ctrl+C
y fin de entrada (Ctrl+D) cierran la sesión con una despedida sin traceback.
Verificado con `python3 -m unittest discover -s tests -v` (20 pruebas en total),
incluyendo una ejecución real del programa con base de datos temporal.

---

## Bloque 10 — Pruebas y ejemplo de interacción

**Objetivo:** Validar el flujo completo.

**Tareas:**
- Ejecutar el diálogo de ejemplo (objetivo → rutina → registro → progreso).
- Probar casos límite (sin registros, comando desconocido, grupo inexistente).
- Corregir errores detectados.

**Hecho cuando:** el ejemplo de interacción completa se reproduce sin fallos.

**Verificado:** ejemplo reproducible en [ejemplos/interaccion.txt](ejemplos/interaccion.txt)
con instrucciones en [ejemplos/README.md](ejemplos/README.md).
`tests/test_flujo_completo.py` ejecuta el CLI real con base temporal, comprueba
objetivo → rutina → registros → historial → progreso → recordatorios y verifica
persistencia al reiniciar. Incluye casos sin registros, grupo inexistente,
comando desconocido y datos inválidos sin inserciones. No se detectaron fallos
en estos escenarios. `python3 -m unittest discover -s tests -v`: 22 pruebas aprobadas.

---

## Bloque 11 — Documentación y modularidad

**Objetivo:** Dejar el código mantenible y documentado.

**Tareas:**
- Confirmar que cada funcionalidad es una función independiente.
- Documentar cada función (docstrings) y el flujo general.
- Verificar que agregar una funcionalidad no obliga a reescribir el resto.

**Hecho cuando:** el proyecto está documentado y las funciones son intercambiables.

**Implementado:** [README.md](README.md) documenta ejecución, comandos, datos,
límites, arquitectura y pasos para ampliar funcionalidades. Todos los módulos y
funciones de la aplicación tienen docstrings, verificados mediante AST.
Se revisó la separación entre CLI, router, funciones de dominio y conexión SQLite;
agregar comandos requiere registrar su intención y ayuda, sin reescribir el bucle.
Se documentaron los contratos de retorno, inicialización y cierre de conexiones,
y la salida directa de la ayuda a revisar en la futura integración con voz.
Verificación: 22 pruebas aprobadas con `python3 -m unittest discover -s tests -v`.

---

## Bloque 12 — Integración con voz (fase posterior)

**Objetivo:** Sumar reconocimiento de voz y respuesta auditiva sobre la lógica ya probada por CLI.

**Tareas:**
- Reemplazar el cuerpo de `escuchar()` por reconocimiento de voz (voz → texto).
- Reemplazar el cuerpo de `hablar()` por síntesis de voz (texto → audio).
- Mantener intacto el resto del código: solo cambian esas dos funciones.
- Permitir alternar entre modo texto y modo voz.

**Hecho cuando:** el agente funciona por voz de extremo a extremo reutilizando toda la lógica del CLI.

**Implementado, pendiente de validación real:** adaptador opcional con
SpeechRecognition (Google, es-AR) y pyttsx3, inicio con `--modo voz` y cambio
mediante `modo texto` / `modo voz`. Se reutiliza la lógica de dominio; el CLI
solo agrega selección de modo y deriva la ayuda a `hablar()`.
Incluye calibración, límites de escucha, separador dictado “punto y coma” y
retorno a texto ante fallos. Instalación y prueba manual en [README.md](README.md).
27 pruebas aprobadas, incluidas 5 de voz con dispositivos y servicios simulados.
Este entorno carece de dispositivos de audio y dependencias opcionales: falta
comprobar reconocimiento y reproducción reales para marcar el bloque completo.

---

## Bloque 13 — Ampliaciones futuras (opcional)

**Objetivo:** Implementar la interfaz gráfica solicitada y dejar las demás mejoras priorizadas.

**Implementado:** interfaz con `tkinter` y `ttk` en `fitness/gui.py`.
Incluye objetivos, rutinas, registro, historial, progreso y recordatorios mediante
formularios y botones, con respuestas y errores en la ventana. Reutiliza las
funciones de dominio y SQLite. Inicio: `python3 main.py --interfaz grafica`;
en Windows: `py main.py --interfaz grafica`. La terminal sigue disponible.

**Verificación:** 30 pruebas en total. En el entorno aislado pasaron 28 y se
omitieron 2 de widgets por falta de acceso a la pantalla. Las 3 pruebas de
`test_gui.py` (incluidas esas 2) pasaron con acceso a la pantalla de Linux.
Se verificaron el flujo por botones, validaciones y recuperación ante errores
de SQLite. Queda pendiente comprobar la presentación en Windows.

**Backlog restante, en orden de prioridad:**
1. Cálculo de volumen de entrenamiento (series × reps × peso).
2. Gráficos de progreso.
3. Perfiles de múltiples usuarios.
4. Conexión con dispositivos o apps de actividad física.

**Hecho cuando:** la interfaz gráfica permite usar las funciones existentes y
las demás mejoras quedan listadas como backlog priorizado.

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
