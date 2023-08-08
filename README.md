# Actualizaciones por OTA
Al cambiar el número de version en el archivo `version.txt` a uno mayor, los archivos dentro de la carpeta `www` y la versión de firmware `micropython.bin` será actualizada a todos los microcontroladores.

# Historial de versiones
* 1.0.0 -> Versión inicial
* 1.0.1 -> Desarrollo
* 2.0.0 -> Versión entregada a youtubers 08/04/22
* 2.0.1 -> Cambio de framesize de 10 a 8
* 2.0.2 -> Versión de lanzamiento (resolución de cámara 1600x1200).
* 2.0.3 -> Cambio de condición de sleep para MQTT y delay para credenciales wifi. Reinicio después de actualizar.
* 2.0.4 -> Framesize en change_settings de rango [0; 13].
* 2.0.5 -> Elimina los tildes en mensajes al Marlin.
* 2.1.0 -> Cambia la forma en que se reciben y transmiten los datos de la impresora (payload).
* 2.2.0 -> Corrige la URL para checkear los flags de Django, deja de utilizar la mac para autenticarse en el broker de MQTT y empieza a utilizar el flag de github para actualizarse.

