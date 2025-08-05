import asyncio
import websockets
import json

async def recibir_datos():
    uri = "ws://192.168.1.149:81"  # Reemplaza XX por la IP real del ESP32
    async with websockets.connect(uri) as websocket:
        print("Conectado al ESP32")
        
        while True:
            mensaje = await websocket.recv()
            print(f"Mensaje recibido: {mensaje}")

            try:
                datos = json.loads(mensaje)
                if "sensor" in datos:
                    valor_sensor = datos["sensor"]
                    print(f"Valor del sensor: {valor_sensor}")
            except json.JSONDecodeError:
                print("No es un JSON válido")

asyncio.run(recibir_datos())
