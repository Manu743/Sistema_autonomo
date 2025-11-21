import websocket
import json

# Dirección del servidor WebSocket
url = "ws://192.168.1.100:881"  # Cambia por la IP de tu ESP32

# Crear la conexión
ws = websocket.WebSocket()
ws.connect(url)
print("Conectado al servidor WebSocket")

# Enviar mensaje
mensaje_a_enviar = "distancia"
ws.send(mensaje_a_enviar)
print("Mensaje enviado:", mensaje_a_enviar)

# Esperar respuesta
try:
    respuesta = ws.recv()  # Bloquea hasta recibir mensaje
    print("Respuesta recibida:", respuesta)
except websocket.WebSocketTimeoutException:
    print("No se recibió respuesta a tiempo")

# Cerrar la conexión
ws.close()
print("Conexión cerrada")
