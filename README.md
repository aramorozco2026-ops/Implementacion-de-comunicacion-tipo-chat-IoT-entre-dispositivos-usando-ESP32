# Proyecto IoT Chat: Comunicación Confiable sobre UDP con MicroPython

Este proyecto implementa un sistema de chat descentralizado (Peer-to-Peer) entre dos placas de desarrollo (como el ESP32 o ESP8266) utilizando **MicroPython**. 

A pesar de que el sistema utiliza el protocolo **UDP** (el cual no garantiza la entrega ni el orden de los paquetes), el script implementa un mecanismo básico de **Control de Errores** inspirado en los protocolos ARQ (*Automatic Repeat-reQuest*). Utiliza una validación de suma de verificación (**Checksum**) y señales de confirmación (**ACK/NACK**) para asegurar que los mensajes lleguen intactos.

##  Características

* **Arquitectura P2P:** Comunicación directa entre dos dispositivos en la misma red local.
* **Multihilo (Multithreading):** Usa el módulo `_thread` para mantener un hilo escuchando de fondo mientras el bucle principal espera la entrada de texto del usuario.
* **Detección de Errores:** Cálculo de Checksum de 8 bits para verificar la integridad de los datos.
* **Manejo de Confirmaciones:**
  * **ACK (Acknowledgment):** Confirmación de que el mensaje llegó correctamente.
  * **NACK (Negative Acknowledgment):** Notificación de que el mensaje llegó corrupto, lo que dispara una **retransmisión automática** desde una memoria caché local (`ultima_trama_correcta`).
* **Simulador de Ruido Integrado:** Permite forzar de manera intencional un error en el Checksum para probar el comportamiento del sistema ante interferencias en la red.

---

##  Estructura de la Trama de Datos

Los datos se empaquetan en cadenas de texto separadas por el carácter pipe (`|`) siguiendo el siguiente formato según el caso:

| Tipo de Trama | Estructura | Descripción |
| :--- | :--- | :--- |
| **DATA** | `DATA|id_mensaje|contenido_mensaje|checksum` | Envío de un mensaje de texto. |
| **ACK** | `ACK|id_mensaje|checksum_id` | Confirmación de recepción exitosa. |
| **NACK** | `NACK|id_mensaje|checksum_id` | Solicitud de retransmisión por datos corruptos. |

---

## ⚙️ Configuración y Requisitos

### Requisitos previos
1. Dos placas de desarrollo compatibles con MicroPython (ej. ESP32).
2. Estar conectados a la misma red Wi-Fi (o un punto de acceso/Hotspot móvil).

### Ajustes en el código
Antes de cargar el archivo `Proyecto_IoT_Chat.py` en tus dispositivos, debes modificar las constantes de red al inicio del script:

```python
# 1. CONFIGURACIÓN DE RED
SSID = 'TU_RED_WIFI'         # Nombre de tu red
PASSWORD = 'TU_CONTRASEÑA'    # Contraseña de tu red
MI_PUERTO = 5000             # Puerto de escucha (debe ser el mismo en ambos)

# Cambia esta IP por la IP asignada al OTRO dispositivo
IP_DESTINO = '192.168.137.X'
