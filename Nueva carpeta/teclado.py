import keyboard
import sys
import asyncio
import websockets


KEY_ACTIONS = {
    'w': "adelante",
    's': "atras",
    'a': "izquierda",
    'd': "derecha"
}

current_action = None

def on_press(event):
    global current_action
    if event.name in KEY_ACTIONS and not current_action:
        current_action = KEY_ACTIONS[event.name]
        print(f"\nPresionaste: {event.name} -> {current_action}")

def on_release(event):
    global current_action
    if event.name in KEY_ACTIONS and current_action == KEY_ACTIONS[event.name]:
        current_action = None
        print(f"\nSoltaste: {event.name} -> DETENIDO")
    
    # Salir con Q
    if event.name == 'q':
        print("\nSaliendo del programa...")
        keyboard.unhook_all()
        sys.exit()

# Configurar listeners
keyboard.hook(on_press)
keyboard.on_release(on_release)

print("Presiona W/A/S/D para mover. Q para salir")

def __init__(self):
        #self.current_key = None
        self.loop = None
        self.websocket = None
        self.stop_event = asyncio.Event()

async def command_handler(self):
    while True:
        if self.current_action:
            command = KEY_ACTIONS[self.current_action]
            try:
                await self.websocket.send(command)
                print(f"Comando enviado: {command}")
                respuesta = await self.websocket.recv()
                print(f"respuesta: {respuesta}")
                await self.stop_event.wait()
                await self.websocket.send("STOP")
                print("Comando STOP enviado")
                self.stop_event.clear()
            except Exception as e:
                print(f"Error: {e}")
                break
        await asyncio.sleep(0.1)

async def connect(self):
    uri = "ws://192.168.1.149:81"  # Cambiar por tu IP
    self.websocket = await websockets.connect(uri)
    print("Conectado. Usa W/A/S/D para mover, Q para salir")
    
    keyboard.on_press(self.on_press)
    keyboard.on_release(self.on_release)
    
    # Iniciar manejador de comandos
    handler_task = asyncio.create_task(self.command_handler())
    
    await asyncio.Future()

# Mantener el programa activo
try:
    keyboard.wait()  # Bloquea hasta que se presione 'q'
finally:
    keyboard.unhook_all(),sys.exit()
    