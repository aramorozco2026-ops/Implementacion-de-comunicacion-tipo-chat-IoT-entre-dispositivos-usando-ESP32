import network
import time
import socket
import _thread

# 1. CONFIGURACIÓN DE RED
SSID = 'GERARDO0517'
PASSWORD = '12345678'
MI_PUERTO = 5000

# Cambia esta IP por la IP del OTRO ESP
IP_DESTINO = '192.168.137.X' 

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print("Conectando al Hotspot...")
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        time.sleep(1)

print("WiFi BIEN, MI IP ES:", wlan.ifconfig()[0])

# 2. PROTOCOLO Y VARIABLES GLOBALES
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', MI_PUERTO))

contador_mensajes = 0
ultima_trama_correcta = ""  # Memoria caché para la retransmisión

def calcular_checksum(texto):
    suma = sum(ord(c) for c in texto)
    return suma % 256

# 3. HILO RECEPTOR (Escucha y Responde)
def hilo_receptor():
    global ultima_trama_correcta
    while True:
        try:
            datos, addr = s.recvfrom(1024)
            trama = datos.decode('utf-8')
            partes = trama.split('|')
            tipo = partes[0]
            
            # --- CASO A: Recibimos un mensaje de chat ---
            if tipo == "DATA":
                msg_id = partes[1]
                payload = partes[2]
                chk_recibido = int(partes[3])
                chk_calculado = calcular_checksum(payload)
                
                # Evaluamos si el mensaje viene intacto
                if chk_calculado == chk_recibido:
                    print(f"\n[Amigo]: {payload}")
                    # Todo bien, enviamos ACK
                    ack_trama = f"ACK|{msg_id}|{calcular_checksum(msg_id)}"
                    s.sendto(ack_trama.encode('utf-8'), addr)
                else:
                    # El checksum no cuadra, simulamos ruido o interferencia
                    print(f"\n[!] ALERTA: Mensaje corrupto. Checksum esperado: {chk_calculado}, Recibido: {chk_recibido}")
                    print(f"[!] Solicitando retransmisión (Enviando NACK)...")
                    nack_trama = f"NACK|{msg_id}|{calcular_checksum(msg_id)}"
                    s.sendto(nack_trama.encode('utf-8'), addr)
                    
            # --- CASO B: Recibimos confirmación de éxito ---
            elif tipo == "ACK":
                msg_id = partes[1]
                print(f"  Entregado (ACK del msj {msg_id})")
                
            # --- CASO C: Nos avisan que nuestro mensaje llegó mal ---
            elif tipo == "NACK":
                msg_id = partes[1]
                print(f"  Error en destino (NACK recibido).")
                print(f"  Retransmitiendo mensaje de forma automática...")
                # Reenviamos la trama que teníamos guardada en caché
                s.sendto(ultima_trama_correcta.encode('utf-8'), addr)
                
        except Exception as e:
            pass
        time.sleep(0.1)

_thread.start_new_thread(hilo_receptor, ())

# 4. BUCLE PRINCIPAL (Envío de mensajes)
print("Escribe un mensaje y presiona Enter.")

while True:
    mensaje = input("")
    if mensaje:
        contador_mensajes += 1
        
        # LÓGICA DE SIMULACIÓN DE ERROR
        if mensaje.startswith("!error "):
            texto_real = mensaje.replace("!error ", "")
            chk_real = calcular_checksum(texto_real)
            
            # Corrompemos el checksum sumándole 5 a propósito
            chk_corrupto = chk_real + 5 
            
            # Guardamos la versión perfecta en la memoria por si piden retransmitir
            ultima_trama_correcta = f"DATA|{contador_mensajes}|{texto_real}|{chk_real}"
            
            # Armamos la trama dañada que vamos a enviar primero
            trama_envio = f"DATA|{contador_mensajes}|{texto_real}|{chk_corrupto}"
            
            print(f"  Simulando ruido: Enviando Checksum {chk_corrupto} en lugar del real ({chk_real})...")
            s.sendto(trama_envio.encode('utf-8'), (IP_DESTINO, MI_PUERTO))
            
        # LÓGICA NORMAL
        else:
            chk = calcular_checksum(mensaje)
            # Guardamos en caché y armamos trama
            ultima_trama_correcta = f"DATA|{contador_mensajes}|{mensaje}|{chk}"
            trama_envio = ultima_trama_correcta
            
            s.sendto(trama_envio.encode('utf-8'), (IP_DESTINO, MI_PUERTO))
            print(f"  Enviando... (Esperando ACK)")