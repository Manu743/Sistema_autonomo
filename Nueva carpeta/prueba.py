import websockets
import asyncio
import keyboard

KEY_COMMANDS = {
    'w': 'adelante',
    's': 'atras',
    'a': 'izquierda',
    'd': 'derecha'
}

class RobotController:
    def __init__(self):
        self.current_key = None
        self.loop = asyncio.get_event_loop()
        self.websocket = None
        self.running = True
        self.command_queue = asyncio.Queue()

    async def command_sender(self):
        while self.running:
            try:
                if self.current_key:
                    command = KEY_COMMANDS[self.current_key]
                    await self.websocket.send(command)
                    print(f"Enviado: {command}")
                await asyncio.sleep(0.1)  # Intervalo de actualización
            except Exception as e:
                print(f"Error de conexión: {e}")
                break

    async def connect(self):
        uri = "ws://192.168.1.149:81"
        try:
            self.websocket = await websockets.connect(uri)
            print("Conexión establecida. Usa W/A/S/D. Q para salir")
            
            # Configurar teclado
            keyboard.hook(self.on_press)
            keyboard.on_release(self.on_release)
            
            # Iniciar tareas
            sender_task = asyncio.create_task(self.command_sender())
            await asyncio.gather(sender_task)
            
        except Exception as e:
            print(f"Error inicial: {e}")
        finally:
            await self.cleanup()

    def on_press(self, event):
        if event.name in KEY_COMMANDS and not self.current_key:
            self.current_key = event.name
            asyncio.run_coroutine_threadsafe(
                self.websocket.send(KEY_COMMANDS[self.current_key]),
                self.loop
            )
            
        if event.name == 'q':
            self.running = False
            keyboard.unhook_all()
            self.loop.call_soon_threadsafe(self.loop.stop)

    def on_release(self, event):
        if event.name == self.current_key:
            self.current_key = None
            asyncio.run_coroutine_threadsafe(
                self.websocket.send("detener"),
                self.loop
            )

    async def cleanup(self):
        if self.websocket:
            await self.websocket.close()
        keyboard.unhook_all()

async def main():
    controller = RobotController()
    await controller.connect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nPrograma finalizado")