# Ejemplo de interacción por terminal

Desde la raíz del proyecto, ejecutá `python3 main.py` e ingresá, en orden,
los comandos de [interaccion.txt](interaccion.txt).

El ejemplo registra un objetivo, consulta piernas y guarda dos entrenamientos
de Sentadillas: 40 y 45 kg, ambos con 3 series de 10 repeticiones.
Después del primer registro, el progreso pide al menos dos registros.
Después del segundo, el historial muestra 45 kg y el progreso indica un aumento
de 5 kg. Las fechas corresponden al momento de ejecución.
Finalmente crea y consulta un recordatorio para las 18:30 y termina con `salir`.

La ejecución manual agrega datos a `fitness.db` en el directorio de ejecución.
El resultado de progreso descrito supone una base nueva: si ya existen registros
de Sentadillas, la comparación parte del primero de esos registros.
Los objetivos y entrenamientos persisten al reiniciar; los recordatorios se
pierden al cerrar y no disparan avisos automáticos.

## Reproducir y verificar sin modificar los datos personales

Desde la raíz del proyecto:

```bash
python3 -m unittest discover -s tests -p 'test_flujo_completo.py' -v
```

Esta prueba lee el mismo archivo de comandos, ejecuta el programa como un proceso
real con una base temporal y verifica las respuestas en orden. Luego inicia una
segunda sesión para comprobar la persistencia y el reinicio de los recordatorios.
Otra prueba verifica grupo inexistente, falta de registros, comando desconocido,
peso negativo, repeticiones fraccionarias y hora inválida, y comprueba que no se
hayan guardado datos inválidos.

Para ejecutar todas las pruebas:

```bash
python3 -m unittest discover -s tests -v
```
