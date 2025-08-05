import sys
import threading
import cv2
import websockets
import asyncio
import keyboard
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

# Configuración de constantes
SERVER_CAMARA = 'http://192.168.1.105/480x320.jpg'
SERVER_WS = "ws://192.168.1.100:81"

class RobotController(QObject):
    command_sent = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.websocket = None
        self.loop = None
        self.running = False
        self._setup_event_loop()

    def _setup_event_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    async def _connect_ws(self):
        try:
            self.websocket = await websockets.connect(SERVER_WS)
            self.command_sent.emit("Conexion WS establecida")
            while self.running:
                await asyncio.sleep(0.1)
        except Exception as e:
            self.command_sent.emit(f"Error WS: {str(e)}")
        finally:
            if self.websocket:
                await self.websocket.close()

    def start_connection(self):
        self.running = True
        asyncio.run_coroutine_threadsafe(self._connect_ws(), self.loop)
        self.loop_thread = threading.Thread(target=self.loop.run_forever, daemon=True)
        self.loop_thread.start()

    async def _send_command(self, command):
        if self.websocket and self.websocket.open:
            await self.websocket.send(command)
            self.command_sent.emit(f"Enviado: {command}")

    def send_command(self, command):
        asyncio.run_coroutine_threadsafe(self._send_command(command), self.loop)

    def stop(self):
        self.running = False
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)

class VideoThread(QThread):
    change_pixmap = pyqtSignal(QImage)
    running = True

    def run(self):
        url = SERVER_CAMARA
        cap = cv2.VideoCapture(url)
        while self.running:
            ret, frame = cap.read()
            if ret:
                frame = cv2.rotate(frame, cv2.ROTATE_180)
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.change_pixmap.emit(qt_image.scaled(640, 480, Qt.KeepAspectRatio))
            QThread.msleep(30)

    def stop(self):
        self.running = False

class ControlWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('./Nueva Carpeta/Control.ui', self)
        
        self.setWindowTitle("Control de Robot")
        self.robot_controller = RobotController()
        self.video_thread = VideoThread()
        self.setup_connections()

    def setup_connections(self):
        self.Conectar.clicked.connect(self.start_connection)
        self.Desconectar.clicked.connect(self.stop_connection)
        self.Adelante.clicked.connect(lambda: self.send_command('adelante'))
        self.Atras.clicked.connect(lambda: self.send_command('atras'))
        self.Izquierda.clicked.connect(lambda: self.send_command('izquierda'))
        self.Derecha.clicked.connect(lambda: self.send_command('derecha'))
        
        self.video_thread.change_pixmap.connect(self.update_image)
        self.robot_controller.command_sent.connect(self.update_status)
        
        keyboard.hook(self.on_key_event)

    def start_connection(self):
        self.video_thread.start()
        self.robot_controller.start_connection()
        print("Sistema conectado")

    def stop_connection(self):
        self.video_thread.stop()
        self.robot_controller.stop()
        print("Sistema desconectado")

    def send_command(self, command):
        self.robot_controller.send_command(command)

    def on_key_event(self, event):
        commands = {
            'w': 'adelante',
            's': 'atras',
            'a': 'izquierda',
            'd': 'derecha'
        }
        if event.event_type == keyboard.KEY_DOWN and event.name in commands:
            self.send_command(commands[event.name])
        elif event.event_type == keyboard.KEY_UP and event.name in commands:
            self.send_command('detener')

    @pyqtSlot(QImage)
    def update_image(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    @pyqtSlot(str)
    def update_status(self, message):
        self.estado.setText(f"Estado: {message}")

    def closeEvent(self, event):
        self.stop_connection()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ControlWindow()
    window.show()
    sys.exit(app.exec_())