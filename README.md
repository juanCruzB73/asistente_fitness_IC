# Asistente virtual de fitness

Aplicación de terminal para guardar objetivos, consultar rutinas, registrar
entrenamientos y comparar el peso utilizado en un ejercicio. Funciona por texto y ofrece un modo de voz opcional, pendiente de validación
con micrófono y altavoces reales. También incluye una interfaz gráfica con Tkinter.

## Ejecutar

El modo texto requiere Python 3 con SQLite y utiliza únicamente la biblioteca estándar.
Desde la raíz del proyecto:

```bash
python3 main.py
```

La primera ejecución crea `fitness.db` en el directorio desde el que se ejecuta
el comando. No requiere instalar dependencias ni servicios externos.

## Ejecutar desde Windows (PowerShell)

### 1. Preparar Python y el proyecto

Instalá Python 3 desde [Python para Windows](https://www.python.org/downloads/windows/).
Abrí una nueva terminal PowerShell y comprobá la instalación:

```powershell
py --version
```

Si `py` no se reconoce pero `python --version` funciona, usá `python` en lugar
de `py` en los comandos siguientes. Para voz, usá Python 3.9 o posterior,
compatible con las dependencias opcionales.

Copiá o descargá el proyecto completo y descomprimilo. Entrá en la carpeta que
contiene `main.py`, reemplazando esta ruta por la de tu equipo:

```powershell
cd "C:\Users\TuUsuario\Documents\asistente_fitness_IC"
```

Si copiaste el proyecto desde Linux, creá un entorno nuevo en Windows: la carpeta
`.venv` de Linux no sirve en Windows. Los archivos del proyecto y `fitness.db`
se pueden conservar.

### 2. Ejecutar por texto

No requiere instalar las dependencias de voz:

```powershell
py main.py --modo texto
```

Cuando aparezca `Tu:`, escribí `piernas` y presioná Enter. Podés escribir
`ayuda` para ver los comandos o `salir` para cerrar. Ctrl+C también termina la
sesión; en la consola de Windows, el fin de entrada se envía con Ctrl+Z y Enter.

### 3. Preparar el modo de voz

Desde la misma carpeta, creá un entorno virtual e instalá las dependencias:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-voz.txt
```

Estos comandos usan directamente el Python del entorno: no hace falta ejecutar
`Activate.ps1` ni cambiar la política de ejecución de PowerShell.
En Windows, [SpeechRecognition instala el soporte de micrófono mediante el extra
audio](https://pypi.org/project/SpeechRecognition/) y
la salida de voz utiliza SAPI5 directamente mediante `pywin32`, con reproducción
síncrona para evitar que se omitan respuestas consecutivas.
Los comandos `sudo apt` y las rutas `.venv/bin/python` de la sección Linux no
corresponden a Windows.

Conectá el micrófono y los altavoces. En la configuración de Windows, buscá
“micrófono”, habilitá el acceso para aplicaciones de escritorio y seleccioná
el dispositivo de entrada que quieras usar como predeterminado.

### 4. Ejecutar por voz

```powershell
.\.venv\Scripts\python.exe main.py --modo voz
```

**El audio se envía a Google para transcribirlo y requiere Internet.**
Mantené silencio durante la calibración. Cuando aparezca “Escuchando”, decí
“quiero ver mi rutina de piernas”. Deberías ver la transcripción y escuchar
la respuesta. Decí “modo texto” para volver al teclado o “salir” para cerrar.
También podés iniciar por texto con el entorno y activar la voz después:

```powershell
.\.venv\Scripts\python.exe main.py --modo texto
```

Dentro del asistente, escribí `modo voz`. Para abrirlo otro día, entrá de nuevo
en la carpeta del proyecto y ejecutá el comando del modo deseado; no necesitás
reinstalar las dependencias.

### 5. Ejecutar las pruebas

```powershell
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -v
```

Si solo usás texto y no creaste el entorno, usá
`py -X utf8 -m unittest discover -s tests -v`. Las pruebas de voz simulan el audio;
la comprobación con micrófono y altavoces reales se realiza por separado.

### Problemas frecuentes en Windows

- **No encuentra `main.py`:** ejecutá `dir` y comprobá que estés dentro de la
  carpeta del proyecto, no en su carpeta contenedora.
- **Falta un módulo:** instalá `requirements-voz.txt` con el mismo
  `.\.venv\Scripts\python.exe` que usás para iniciar el programa.
- **Falla la instalación de PyAudio:** revisá que haya una distribución
  compatible con tu versión y arquitectura de Python; el modo texto puede
  seguir usándose mientras resolvés la instalación de audio.
- **No detecta el micrófono:** comprobá permisos, dispositivo predeterminado y
  que funcione en la grabadora de Windows. Ante un fallo el asistente vuelve a texto.
- **No se escucha o pronuncia mal:** revisá el volumen y las voces españolas
  instaladas en Windows. El programa usa una voz española disponible o la
  predeterminada si no encuentra ninguna.
- **Caracteres extraños en la terminal:** probá iniciar con
  `.\.venv\Scripts\python.exe -X utf8 main.py --modo texto`.

La ejecución en Windows y el audio real todavía no se verificaron en este
entorno de desarrollo Linux. La base se guarda en el directorio de ejecución:
iniciá siempre desde la misma carpeta para consultar los mismos registros.

## Interfaz gráfica con Tkinter

Desde la raíz del proyecto, abrí la ventana:

```bash
python3 main.py --interfaz grafica
```

En Windows (PowerShell):

```powershell
py main.py --interfaz grafica
```

Si ya creaste el entorno virtual en Windows:

```powershell
.\.venv\Scripts\python.exe main.py --interfaz grafica
```

La ventana tiene cuatro pestañas:

- **Objetivo y rutinas:** guardar o consultar tu objetivo y elegir un grupo muscular.
- **Entrenamiento:** ingresar ejercicio, peso en kg, repeticiones y series.
- **Historial y progreso:** consultar el último entrenamiento o comparar pesos.
  Al guardar un entrenamiento, su nombre queda preparado para estas consultas.
- **Recordatorios:** agregar una hora y mensaje y consultar la lista de la sesión.

Las confirmaciones y los errores aparecen en el panel inferior de respuestas.
Podés navegar por los campos con Tab y cerrar mediante el botón Cerrar o la X.
Los formularios usan las mismas validaciones y `fitness.db` que la terminal;
iniciá ambas interfaces desde la misma carpeta para compartir registros.
Los recordatorios siguen siendo temporales y no generan avisos automáticos.
La interfaz gráfica usa texto; el reconocimiento y la síntesis de voz se
mantienen disponibles en la terminal con `--modo voz`.

Tkinter es un componente opcional de Python, no se instala con `pip`.
En Windows, si falta, modificá la instalación de Python para incluir Tcl/Tk.
En Debian/Ubuntu podés instalarlo con `sudo apt install python3-tk`.
`py -m tkinter` en Windows o `python3 -m tkinter` en Linux permite comprobarlo
abriendo una ventana de demostración; véase la
[documentación oficial de Tkinter](https://docs.python.org/3/library/tkinter.html).
Si no hay pantalla disponible, usá `--interfaz terminal`.

Las pruebas de `tests/test_gui.py` ejecutan formularios con widgets reales y una
base temporal. Se omiten automáticamente si no hay Tkinter o pantalla.
Se verificaron en Linux; la presentación en Windows queda por comprobar.

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
| `fitness/gui.py` | Ventana Tkinter, formularios y presentación de respuestas |
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

La voz se implementa en `fitness/voz.py`, sin modificar las funciones de dominio.
La interfaz gráfica llama directamente a esas funciones y usa el contexto
`usar_salida(receptor)` para mostrar sus respuestas en la ventana. Al terminar
cada acción se restaura la salida anterior, incluso si ocurre un error.
`configurar_modo()` carga las dependencias opcionales y devuelve si pudo activar
el modo solicitado. `escuchar()` transcribe y `hablar()` muestra y sintetiza las
respuestas, incluida la ayuda. Los diagnósticos de audio se muestran en terminal.

El avance y las etapas pendientes están en [PLAN_DE_TRABAJO.md](PLAN_DE_TRABAJO.md).


## Modo de voz (opcional)

Utiliza [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) para
transcribir con Google. La síntesis local usa SAPI5 mediante `pywin32` en Windows
y [pyttsx3](https://pypi.org/project/pyttsx3/) en los demás sistemas.
**Al activar voz, el audio se envía a Google y se necesita Internet.**
Se usa el micrófono predeterminado y reconocimiento en español de Argentina
(`es-AR`). Se selecciona una voz española instalada si está disponible; de lo
contrario se mantiene la voz predeterminada del sistema.

En Debian/Ubuntu, instalá los componentes del sistema:

```bash
sudo apt install python3-venv python3-dev portaudio19-dev espeak-ng libespeak1
```

Desde la raíz del proyecto, creá un entorno e instalá las dependencias opcionales:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-voz.txt
.venv/bin/python main.py --modo voz
```

Para comenzar por teclado: `.venv/bin/python main.py --modo texto`. Dentro de
la sesión, `modo voz` y `modo texto` cambian la entrada y salida sin perder datos.
La voz empieza a escuchar después de terminar cada respuesta. Mantené silencio
durante la calibración inicial y hablá cuando aparezca “Escuchando”.

Decí “quiero ver mi rutina de piernas”, “cuál es mi objetivo” o “salir”. Para
los comandos con separadores, dictá “punto y coma”; el adaptador lo convierte a
`;`. Por ejemplo: “registrar sentadillas punto y coma 40 punto y coma 10 punto y
coma 3”. El servicio debe transcribir los números en cifras para que el validador
existente los acepte; no se convierten números escritos como palabras.
También podés decir «registrar sentadillas con 40 kilos, 10 repeticiones y 3
series», «registrar sentadillas 40 10 3» o simplemente «registrar» para que el
asistente pregunte cada dato por separado. Si la transcripción junta números
(por ejemplo, `4010 3`), se inicia ese registro guiado sin intentar adivinarlos.
El registro guiado pide confirmación antes de guardar; podés decir «cancelar»
en cualquier paso. Los números deben transcribirse en cifras.

La transcripción se muestra antes de procesarla y se ejecuta como un comando
escrito, por lo que conviene revisar los datos confirmados por el agente.

Cada escucha espera hasta 5 segundos para comenzar y captura hasta 15 segundos.
El silencio o audio incomprensible permiten reintentar. Si fallan el dispositivo,
la red o la síntesis, el programa vuelve al teclado. Ctrl+C termina la sesión.


