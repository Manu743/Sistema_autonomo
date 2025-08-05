#para graficos
from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtGui import QImage, QPixmap
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QUrl, QThread, Qt
from PyQt5.uic import loadUi 
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel


import sys
import time
import cv2
import cv2.aruco as aruco
import requests
import queue
import warnings
import pathlib
import sqlite3
import websocket
import json
import threading
import requests
import asyncio
import websockets
import queue
import numpy as np
import torch
import pathlib

# Setup YOLO model
torch.backends.cudnn.benchmark = True
pathlib.PosixPath = pathlib.WindowsPath
model = torch.hub.load('ultralytics/yolov5', 'custom', path='C:/1/bestn.pt', force_reload=False, source='github')
names = model.names
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, message=".*torch.cuda.amp.autocast.*")

# Shared resources
command_queue = queue.Queue()
stop_event = threading.Event()

db = "datos.db"

# datos de la grilla
grilla_dato = [ [0 for _ in range(5) ] for _ in range(5) ]

class base:
    @staticmethod
    def Obtener_Robot(cod_Robot):
        conn = sqlite3.connect(db)
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Robot WHERE cod_Robot = ?", (cod_Robot,))
            return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def Obtener_Area(cod_Area):
        conn = sqlite3.connect(db)
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Area WHERE cod_Area = ?", (cod_Area,))
            return cur.fetchone()
        finally:
            conn.close()

class control(QMainWindow):
    def __init__(self, codigo, codarea):
        super(control, self).__init__()
        self.codigo = codigo
        self.area = codarea
        loadUi('./Control/Contro-Manuall.ui', self)
        datos = base.Obtener_Robot(self.codigo)
        ac = "Activo"
        self.Nombre_2.setText(datos[1])
        self.Nombre_2.setAlignment(Qt.AlignLeft)
        self.Estado.setText(ac)
        self.Estado.setAlignment(Qt.AlignLeft)
        self.IpRobot.setText(datos[6])
        self.IpRobot.setAlignment(Qt.AlignLeft)
        self.IpCamara.setText(datos[7])
        self.IpCamara.setAlignment(Qt.AlignLeft)
        # Conexiones de UI
        self.Autonomo.clicked.connect(lambda:self.desconectar())
        self.Autonomo.clicked.connect(lambda:self.camara_autonoma())
        self.cargarArea.clicked.connect(lambda: self.previsualizar())
        self.Conectar.clicked.connect(lambda:self.desconectar())
        self.Conectar.clicked.connect(lambda:self.start_video())
        self.Detener.clicked.connect(lambda:self.desconectar())
        self.Recorrido_On.clicked.connect(lambda:self.recorrer())
        self.Recorrido_Off.clicked.connect(lambda:self.detener())

        # Atributos de hilos
        self.Work = None
        self.video_worker = None
        self.sensor = None
        self.ws = None

    def start_video(self):
        if self.Work:
            self.Work.scanning = True
            return
        self.Work = Work(self.codigo)
        self.Work.frame_ready.connect(self.update_frames)
        self.Work.command_ready.connect(self.enqueue_command)
        self.Work.start()
        

    def camara_autonoma(self):
       if self.video_worker:
           self.video_worker.scanning = True
           return
       self.video_worker = VideoWorker(self.codigo)
       self.video_worker.frame_ready.connect(self.update_frames)
       self.video_worker.command_ready.connect(self.enqueue_command)
       self.video_worker.start()

    def update_frames(self, frame_air, frame_esp):
        def to_qpixmap(frame):
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            return QPixmap.fromImage(qimg).scaled(400, 296, QtCore.Qt.KeepAspectRatio)
        self.Mapa.setPixmap(to_qpixmap(frame_air))
        self.Camara.setPixmap(to_qpixmap(frame_esp))

    def enqueue_command(self, cmd):
        if cmd:
            command_queue.put(cmd)

    def Imageupd_slot(self, Image):
        self.label.setPixmap(QPixmap.fromImage(Image))

    def desconectar(self):
        # Para video manual
        if self.Work:
            self.Work.stop()
            self.Work.wait()
            self.Work = None
        # Para video autonomo
        if self.video_worker:
            self.video_worker.stop()
            self.video_worker.wait()
            self.video_worker = None

    def previsualizar(self):
        print("cambio de camara a mapa imagen")

    def closeEvent(self, event):
        # Parar todos los hilos al cerrar ventana
        stop_event.set()
        if self.Work:
            self.Work.stop()
            self.Work.wait()
        if self.video_worker:
            self.video_worker.stop()
            self.video_worker.wait()
        if self.sensor:
            self.sensor.stop()
            self.sensor.join()
        if self.ws:
            self.ws.cerrar_ws()
        event.accept()

    def recorrer(self):
        self.video_worker.iniciar_recorrido()

    def detener(self):
        self.video_worker.detener_recorrido()

class Work(QThread):
    frame_ready = pyqtSignal(np.ndarray, np.ndarray)  # frame_air, frame_esp
    command_ready = pyqtSignal(str)

    def __init__(self, codigo):
        super().__init__()
        datos = base.Obtener_Robot(codigo)
        self.cam_ip = datos[7]  # IP ESP32-CAM
        print(self.cam_ip)
        self.scanning = True

        self.cap_air = cv2.VideoCapture(0)  # Cámara aérea
        self.esp_stream = ESP32CamStream(f'http://{self.cam_ip}/')
        self.esp_stream.start()

    def run(self):
        while self.scanning and not stop_event.is_set():
            ret_air, frame_air = self.cap_air.read()
            frame_esp = self.esp_stream.read()
            if not ret_air or frame_esp is None:
                continue

            # Aquí puedes agregar lógica adicional para análisis y comandos
            comando = "adelante"  # por ejemplo (simplificado)

            self.frame_ready.emit(frame_air, frame_esp)
            self.command_ready.emit(comando)
            QtCore.QThread.msleep(100)

        self.esp_stream.stop()
        self.cap_air.release()
        command_queue.put(None)

    def stop(self):
        self.scanning = False
        #self.esp_stream.stop()
        self.quit()
        self.wait()

#Conexion Websocket
class WebSocketClient:
    def __init__(self, ip_robot):
        self.url = f"ws://{ip_robot}:81"
        self.ws = None
        self.connected = False
        self.lock = threading.Lock()
        self.sensor_valor = None

    def connect(self):
        def on_open(ws):
            print("WebSocket abierto")
            self.connected = True

        def on_close(ws, code, msg):
            print("WebSocket cerrado")
            self.connected = False

        def on_error(ws, error):
            print("WebSocket error:", error)
            self.connected = False
            
        def on_message(ws,message):
            try:
                data = json.loads(message)
                if "sensor" in data:
                    self.sensor_valor = int(data['sensor'])
                    print(f"sensor: {data['sensor']} ")
            except json.JSONDecodeError:
                print("codigo invalido: ",message)

        def run():
            websocket.enableTrace(False)
            self.ws = websocket.WebSocketApp(
                self.url,
                on_open=on_open,
                on_close=on_close,
                on_error=on_error,
                on_message=on_message
            )  
            self.ws.run_forever()

        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()

    def enviar_comando(self, comando):
        if self.ws and self.connected:
            try:
                with self.lock:
                    self.ws.send(comando)
                    print(f"Comando enviado: {comando}")
                    time.sleep(0.5)
            except Exception as e:
                print("Error enviando comando:", e)
        else:
            print("WebSocket no conectado")

    def cerrar_ws(self):
        if self.ws:
            self.ws.close()
        self.connected = False

class VideoWorker(QThread):
    frame_ready = pyqtSignal(np.ndarray, np.ndarray)
    command_ready = pyqtSignal(str)


    def __init__(self, codigo):
        super().__init__()
        self.loop = asyncio.get_event_loop()
        # Cargar parámetros de calibración desde calibracion_camera.npz
        calib_data = np.load("C:/Users/maren/OneDrive/Desktop/Proyecto/Diseño/Control/calibracion_camera.npz")
        self.camera_matrix = calib_data["camera_matrix"]
        self.dist_coeffs = calib_data["dist_coeffs"]

        # Diccionario y parámetros ArUco
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.aruco_params = cv2.aruco.DetectorParameters()

        # Tamaño del marcador ArUco en metros (ajusta según tu setup real)
        self.marker_length = 0.05  # por ejemplo, 5 cm

        # Tamaño de la grilla (personaliza si deseas)
        self.grid_rows = 5
        self.grid_cols = 5
        datos = base.Obtener_Robot(codigo)
        self.cam_ip = datos[7]
        self.esp_stream = ESP32CamStream(f'http://{self.cam_ip}/')
        self.running = True

        self.recorrido_activo = False
        self.recorrido_thread = threading.Thread(target=self.recorrer_grilla, daemon=True)
        self.ws = WebSocketClient(datos[6])
        self.obstaculo = False
        self.giro = False

    def recorrer_grilla(self):
        if self.recorrido_activo:
            return
        self.recorrido_activo = True
        print("Iniciando recorrido")
        aux = True
        for fila in range(0,5):
            #columnas = range(1, self.grid_cols) if fila == 0 else (range(self.grid_cols) if fila % 2 == 0 else reversed(range(self.grid_cols)))
            columnas = range(1,5) if fila == 0 else (range(1,5) if fila % 2 == 0 else reversed(range(0,4)))
            print(columnas)
            for col in columnas:
                if not self.recorrido_activo:
                    break
                if self.obstaculo:
                    print("entra a evadir")
                    if col < 5 and fila < 5 and col > 0 and fila >= 0 :
                        print("obstaculo registrado")
                        if aux:
                            grilla_dato[fila][col] = 2
                            self.ws.enviar_comando("derecha")
                            time.sleep(2)
                            self.ws.enviar_comando("adelante2")
                            time.sleep(2)
                            self.ws.enviar_comando("izquierda")
                            time.sleep(2)
                            self.ws.enviar_comando("adelante")
                            time.sleep(2)
                            self.ws.enviar_comando("adelante")
                            time.sleep(2)
                            self.ws.enviar_comando("izquierda")
                            time.sleep(2)
                            print(f"recorrido moviendose a celda({fila},{col+1})")
                            sensor = self.ws.sensor_valor 
                            if sensor is not None and sensor > 3000:
                                grilla_dato[fila][col+1] = 3
                                self.ws.sensor_valor = 0
                                print("registrado mina")
                            else:    
                                grilla_dato[fila][col+1] = 1
                            self.ws.enviar_comando("adelante2")
                            time.sleep(2)
                            self.ws.enviar_comando("derecha")
                            time.sleep(2)
                            self.obstaculo = False
                        else:
                            grilla_dato[fila][col] = 2
                            self.ws.enviar_comando("izquierda")
                            time.sleep(2)
                            self.ws.enviar_comando("adelante2")
                            time.sleep(2)
                            self.ws.enviar_comando("derecha")
                            time.sleep(2)
                            self.ws.enviar_comando("adelante")
                            time.sleep(2)
                            self.ws.enviar_comando("adelante")
                            time.sleep(2)
                            self.ws.enviar_comando("derecha")
                            time.sleep(2)
                            print(f"recorrido moviendose a celda({fila},{col-1})")
                            sensor = self.ws.sensor_valor 
                            if sensor is not None and sensor > 3000:
                                grilla_dato[fila][col-1] = 3
                                self.ws.sensor_valor = 0
                                print("registrado mina")
                            else:    
                                grilla_dato[fila][col-1] = 1
                            self.ws.enviar_comando("adelante2")
                            time.sleep(2)
                            self.ws.enviar_comando("izquierda")
                            time.sleep(2)
                            self.obstaculo = False
                else:
                    if not self.giro:
                        print(f"recorrido moviendose a celda({fila},{col})")
                        sensor = self.ws.sensor_valor 
                        if sensor is not None and sensor > 3000:
                            grilla_dato[fila][col-1] = 3
                            self.ws.sensor_valor = 0
                            print("registrado mina")
                        else:    
                            grilla_dato[fila][col] = 1

                        self.ws.enviar_comando("adelante")
                        time.sleep(3)
                    else:
                        self.giro=False

            if not self.recorrido_activo:
                break
            if aux:
                print(f"recorrido moviendose a celda({fila+1},{col})")                
                self.ws.enviar_comando("derecha")
                time.sleep(2)
                self.ws.enviar_comando("adelante2")
                time.sleep(2)
                sensor = self.ws.sensor_valor 
                if sensor is not None and sensor > 3000:
                    if fila == 4 and col == 4:
                        print("Fin")
                    else:    
                        grilla_dato[fila+1][col] = 3
                        self.ws.sensor_valor = 0
                        print("registrado mina")
                else:
                    if fila == 4 and col == 4:
                        print("Fin")
                    else:    
                        grilla_dato[fila+1][col] = 1
                self.ws.enviar_comando("derecha")
                time.sleep(2)
                aux = False
            else:
                print(f"recorrido moviendose a celda({fila+1},{col})")
                self.ws.enviar_comando("izquierda")
                time.sleep(2)
                self.ws.enviar_comando("adelante2")
                time.sleep(2)
                sensor = self.ws.sensor_valor 
                if sensor is not None and sensor > 3000:
                    grilla_dato[fila+1][col] = 3
                    self.ws.sensor_valor = 0
                    print("registrado mina")
                else:    
                    grilla_dato[fila+1][col] = 1
                self.ws.enviar_comando("izquierda")
                time.sleep(2)
                aux= True

        print("Recorrido Finalizado ")
        self.recorrido_activo = False
        print("Imprimiendo los pesos")
        for i in range(5):
            for j in range(5):
                print(str(grilla_dato[i][j]), end="")
            print("")

    def iniciar_recorrido(self):
        self.ws.connect()
        time.sleep(2)
        if not self.recorrido_thread.is_alive():
            self.recorrido_thread = threading.Thread(target=self.recorrer_grilla, daemon=True)
            self.recorrido_thread.start()
    
    def detener_recorrido(self):
        self.ws.cerrar_ws()
        self.recorrido_activo = False

    def run(self):
        self.esp_stream.start()
        cap_air = cv2.VideoCapture(0)

        while self.running and not stop_event.is_set():
            ret_air, frame_air = cap_air.read()
            if ret_air:
               # Dibujo de grilla con líneas exactas
                h, w = frame_air.shape[:2]
                cell_w = w / self.grid_cols
                cell_h = h / self.grid_rows

                # Dibujar líneas verticales (de 0 a grid_cols)
                for i in range(self.grid_cols + 1):  # +1 para incluir el borde derecho
                    x = int(round(i * cell_w))
                    cv2.line(frame_air, (x, 0), (x, h), (0, 255, 0), 1)  # verde

                # Dibujar líneas horizontales (de 0 a grid_rows)
                for j in range(self.grid_rows + 1):  # +1 para incluir el borde inferior
                    y = int(round(j * cell_h))
                    cv2.line(frame_air, (0, y), (w, y), (0, 255, 0), 1)
                x0 = int(round(0 * cell_w))
                y0 = int(round(0 * cell_h))
                x1 = int(round(1 * cell_w))
                y1 = int(round(1 * cell_h))
                cx = (x0 + x1) // 2
                cy = (y0 + y1) // 2
                cv2.circle(frame_air, (cx, cy), radius=10, color=(0, 0, 255), thickness=-1)
                cv2.circle(frame_air, (cx, cy), radius=10, color=(0, 0, 255), thickness=-1)

                # Detección de ArUco
                gray = cv2.cvtColor(frame_air, cv2.COLOR_BGR2GRAY)
                corners, ids, _ = aruco.detectMarkers(gray, self.aruco_dict, parameters=self.aruco_params)

                if ids is not None:
                    aruco.drawDetectedMarkers(frame_air, corners, ids)
                    rvecs, tvecs, _ = aruco.estimatePoseSingleMarkers(
                        corners, self.marker_length, self.camera_matrix, self.dist_coeffs
                    )

                    for i in range(len(ids)):
                        rvec = rvecs[i]
                        tvec = tvecs[i]
                        R, _ = cv2.Rodrigues(rvec)
                        dir_vector = R @ np.array([1, 0, 0])
                        origin = tvec[0]
                        tip = origin + dir_vector * 0.05

                        pts, _ = cv2.projectPoints(
                            np.array([origin, tip]), np.zeros(3), np.zeros(3), self.camera_matrix, self.dist_coeffs
                        )
                        pt1 = tuple(np.int32(pts[0].ravel()))
                        pt2 = tuple(np.int32(pts[1].ravel()))
                        cv2.arrowedLine(frame_air, pt1, pt2, (255, 0, 255), 3, tipLength=0.3)

                        marker_corners = corners[i][0]
                        cx = int(np.mean(marker_corners[:, 0]))
                        cy = int(np.mean(marker_corners[:, 1]))
                        cv2.circle(frame_air, (cx, cy), 5, (0, 255, 0), -1)

                        col = cx // cell_w
                        row = cy // cell_h
                        if 0 <= row < self.grid_rows and 0 <= col < self.grid_cols:
                            cv2.putText(frame_air, f"Celda: ({row},{col})", (cx + 10, cy - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            # Mostrar frame aéreo en su label
            frame_air_rgb = cv2.cvtColor(frame_air, cv2.COLOR_BGR2RGB)
            qt_img_air = QImage(frame_air_rgb.data, frame_air_rgb.shape[1], frame_air_rgb.shape[0], QImage.Format_RGB888)
            #self.label_air.setPixmap(QPixmap.fromImage(qt_img_air))

            frame_esp = self.esp_stream.read()
            if not ret_air or frame_esp is None:
                continue

            # === Detección con YOLOv5 en frame_esp ===
            alto, ancho = frame_esp.shape[:2]
            cx, cy = ancho // 2, alto // 2
            w_zona, h_zona = 150, 150

            zona_frontal = (cx - w_zona // 2, cy - h_zona // 2, cx + w_zona // 2, cy + h_zona // 2)
            zona_izquierda = (0, cy - h_zona // 2, cx - w_zona // 2, cy + h_zona // 2)
            zona_derecha = (cx + w_zona // 2, cy - h_zona // 2, ancho, cy + h_zona // 2)

            detect = model(frame_esp)
            info = detect.xyxy[0].cpu().numpy()

            obstaculo_frontal = obstaculo_izq = obstaculo_der = False

            for det in info:
                x1, y1, x2, y2, conf, cls = map(int, det[:6])
                nombre = names[cls]
                cx_det = (x1 + x2) // 2
                cy_det = (y1 + y2) // 2

                cv2.rectangle(frame_esp, (x1, y1), (x2, y2), (0,255,0), 2)
                cv2.putText(frame_esp, nombre, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
                cv2.circle(frame_esp, (cx_det, cy_det), 5, (0, 0, 255), -1)

                if zona_frontal[0] <= cx_det <= zona_frontal[2] and zona_frontal[1] <= cy_det <= zona_frontal[3]:
                    obstaculo_frontal = True
                    self.obstaculo = True
                    self.giro = True
                    cv2.putText(frame_esp, f"🔴 {nombre} en zona frontal", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                if zona_izquierda[0] <= cx_det <= zona_izquierda[2]:
                    self.obstaculo = False
                    obstaculo_izq = True
                if zona_derecha[0] <= cx_det <= zona_derecha[2]:
                    self.obstaculo = False
                    obstaculo_der = True

            # Dibujar zonas
            cv2.rectangle(frame_esp, (zona_frontal[0], zona_frontal[1]), (zona_frontal[2], zona_frontal[3]), (255,0,0), 2)
            cv2.rectangle(frame_esp, (zona_izquierda[0], zona_izquierda[1]), (zona_izquierda[2], zona_izquierda[3]), (0,255,255), 1)
            cv2.rectangle(frame_esp, (zona_derecha[0], zona_derecha[1]), (zona_derecha[2], zona_derecha[3]), (0,255,255), 1)

            # Comando de ejemplo
            comando = ""
            if obstaculo_frontal:
                comando = "obstaculo_frontal"
            elif obstaculo_izq:
                comando = "obstaculo_izquierda"
            elif obstaculo_der:
                comando = "obstaculo_derecha"
            else:
                comando = "libre"

            self.frame_ready.emit(frame_air, frame_esp)
            self.command_ready.emit(comando)
            self.msleep(100)

        cap_air.release()
        self.esp_stream.stop()
        command_queue.put(None)

    def stop(self):
        self.running = False
        #self.esp_stream.stop()
        self.quit()
        self.wait()

    

class ESP32CamStream:
    def __init__(self, url):
        self.url = url
        self.frame = None
        self.running = False
        self.lock = threading.Lock()

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self.update_stream, daemon=True)
        self.thread.start()

    def update_stream(self):
        while self.running:
            try:
                response = requests.get(self.url, timeout=0.5, stream=True)
                if response.status_code == 200:
                    bytes_img = b''
                    for chunk in response.iter_content(chunk_size=1024):
                        bytes_img += chunk
                        a = bytes_img.find(b'\xff\xd8')
                        b = bytes_img.find(b'\xff\xd9')
                        if a != -1 and b != -1:
                            jpg = bytes_img[a:b+2]
                            bytes_img = bytes_img[b+2:]
                            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                            if img is not None:
                                with self.lock:
                                    self.frame = img
            except:
                pass

    def read(self):
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def stop(self):
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = control(codigo=1, codarea=1)
    window.show()
    sys.exit(app.exec_())
